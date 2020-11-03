import logging
import json
from asyncio import (
    CancelledError, create_task, get_running_loop, sleep, open_connection,
    wait_for)
from collections import defaultdict

from vogol.gst import stop_pipelines
from vogol.previews import preview_pipeline

log = logging.getLogger(__name__)


class Voctomix:
    def __init__(self, host, presets, broadcaster, gst_pipelines):
        self.host = host
        self.presets = presets
        self.control = VoctomixControl(host, self)
        self.preview_tasks = {}
        self.reconnection_task = None
        self.broadcaster = broadcaster
        self.gst_pipelines = gst_pipelines

    async def connect(self, reconnect_on_error=False):
        """Connect to control, and optionally reconnect forever"""
        if reconnect_on_error:
            self.reconnection_task = create_task(self.maintain_connection())
        else:
            await self._connect()

    async def maintain_connection(self, timeout=5):
        while True:
            try:
                await wait_for(self._connect(), timeout)
                await self.control.disconnection
            except CancelledError:
                return
            except Exception as e:
                log.error("Failed to connect: %s", e)
            await sleep(5)
            await self._disconnect()

    async def _connect(self):
        await self.control.connect()
        await self.connect_previews()

    async def disconnect(self):
        """Disconnect and stop any reconnection attempts"""
        if self.reconnection_task and not self.reconnection_task.done():
            self.reconnection_task.cancel()
        await self._disconnect()

    async def _disconnect(self):
        await stop_pipelines(self.gst_pipelines.values())
        for task in self.preview_tasks.values():
            task.cancel()
        await self.control.disconnect()

    async def connect_previews(self):
        """Start tasks to generate previews from all the mirror ports"""
        sources = self.state['sources']
        ports = [(source, i + 13000) for i, source in enumerate(sources)]
        ports.append(('room', 11000))
        for source, port in ports:
            self.preview_tasks[source] = create_task(
                self.preview_task(source, port))

    async def preview_task(self, source, port):
        """Start and monitor a preview pipeline"""
        while True:
            await preview_pipeline(
                self.host, port, source, self.broadcaster, self.gst_pipelines)
            await sleep(5)

    @property
    def state(self):
        return self.control.state

    def source_port(self, source):
        return 10000 + self.state['sources'].index(source)

    @property
    def mix_audiocaps(self):
        return self.control.config['mix']['audiocaps']

    @property
    def mix_videocaps(self):
        return self.control.config['mix']['videocaps']

    async def action(self, action, source=None, mode=None, volume=None,
                     preset=None):
        """Fire an action requested by the client"""
        send = self.control.send
        if action == 'fullscreen':
            await send('set_videos_and_composite', source, '*', 'fullscreen')
        elif action == 'fullscreen_solo':
            await send('set_videos_and_composite', source, '*', 'fullscreen')
            for other_source, level in self.state['audio'].items():
                if source == other_source and level < 0.2:
                    await send('set_audio_volume', source, '1')
                if source != other_source and level > 0.2:
                    await send('set_audio_volume', other_source, '0')
        elif action == 'preset':
            preset_def = self.presets[preset]
            await send('set_video_a', preset_def.video_a)
            if preset_def.video_b:
                await send('set_video_b', preset_def.video_b)
            await send('set_composite_mode', preset_def.composite_mode)
            for source, level in self.state['audio'].items():
                if source in preset_def.audio_solo and level < 0.2:
                    await send('set_audio_volume', source, '1')
                if source not in preset_def.audio_solo and level > 0.2:
                    await send('set_audio_volume', source, '0')
        elif action == 'set_composite_mode':
            await send('set_composite_mode', mode)
        elif action == 'set_a':
            await send('set_video_a', source)
        elif action == 'set_b':
            await send('set_video_b', source)
        elif action == 'stream_live':
            await send('set_stream_live')
        elif action == 'stream_blank':
            await send('set_stream_blank', 'nostream')
        elif action == 'stream_loop':
            await send('set_stream_blank', 'loop')
        elif action == 'set_audio_volume':
            await send('set_audio_volume', source, str(volume))
        elif action == 'mute':
            await send('set_audio_volume', source, '0')
        elif action == 'unmute':
            await send('set_audio_volume', source, '1')
        elif action == 'cut':
            await send('message', 'cut')
        else:
            raise Exception(f'Unknown action: {action}')

    def state_changed(self, state):
        self.broadcaster.broadcast({'type': 'voctomix_state', 'state': state})


class VoctomixControl:
    def __init__(self, host, voctomix):
        self.host = host
        # A Future that is pending as long as we're connected:
        self.disconnection = None
        self.loop = get_running_loop()
        # Our view of Voctocore's state:
        self.state = {}
        self.reader_task = None
        # Responses that we're .expect()ing from the core:
        self.response_futures = defaultdict(list)
        self.voctomix = voctomix

    async def connect(self):
        """Initialize state, and connect to voctocore"""
        log.info('Connecting to voctomix control')
        self._reader, self._writer = await open_connection(self.host, 9999)
        log.debug('Connected')
        self.disconnection = self.loop.create_future()
        self.state.clear()
        self.reader_task = create_task(self.reader())

        # Initialize our state
        await self.send('get_config')
        await self.send('get_audio')
        await self.send('get_stream_status')
        await self.send('get_composite_mode_and_video_status')
        self.state['connected'] = True

    async def disconnect(self, reason=None):
        """Disconnect from voctocore"""
        if not self.disconnection or self.disconnection.done():
            return
        log.warn('Disconnecting from voctomix control for %s', reason)
        self.state['connected'] = False
        for futures in self.response_futures.values():
            for future in futures:
                if not future.done():
                    future.cancel()
        self.response_futures.clear()
        if self.reader_task and not self.reader_task.done():
            self.reader_task.cancel()
        if not self._writer.is_closing():
            self._writer.close()
        self.disconnection.set_result(reason)

    async def reader(self):
        """Follow events from the core

        They can arrive at any time.
        If anyone is waiting for one of them, notify them.
        """
        while not self._reader.at_eof():
            try:
                line = await self._reader.readline()
            except (ConnectionResetError, CancelledError) as e:
                await self.disconnect(e)
                return
            line = line.decode('utf-8').strip()
            try:
                cmd, args = line.split(None, 1)
            except ValueError:
                continue
            self.update_state(cmd, args)
            futures = self.response_futures[cmd]
            while futures:
                future = futures.pop(0)
                future.set_result(args)
            self.voctomix.state_changed(self.state)

        await self.disconnect(EOFError)

    async def send(self, *command):
        """Send a command to voctomix"""
        last_responses = {
            'get_audio': 'audio_status',
            'get_config': 'server_config',
            'get_composite_mode_and_video_status':
                'composite_mode_and_video_status',
            'get_stream_status': 'stream_status',
            'message': 'message',
            'set_audio_volume': 'audio_status',
            'set_composite_mode': 'composite_mode_and_video_status',
            'set_stream_blank': 'stream_status',
            'set_stream_live': 'stream_status',
            'set_stream_loop': 'stream_status',
            'set_video_a': 'video_status',
            'set_video_b': 'video_status',
            'set_videos_and_composite': 'composite_mode_and_video_status',
        }
        completion = self.expect(last_responses[command[0]])

        cmd = ' '.join(command)
        self._writer.write(cmd.encode('utf-8'))
        self._writer.write(b'\n')
        await self._writer.drain()

        return await completion

    async def expect(self, command):
        """Wait for a particular response from voctomix"""
        future = self.loop.create_future()
        self.response_futures[command].append(future)
        return await future

    def update_state(self, cmd, args):
        """Update our view of Voctomix's state, based on a received message"""
        if cmd == 'server_config':
            self.config = json.loads(args)
            self.state['sources'] = self.config['mix']['sources'].split(',')
        elif cmd == 'audio_status':
            self.state['audio'] = json.loads(args)
        elif cmd == 'composite_mode_and_video_status':
            mode, a, b = args.split()
            self.state['video_a'] = a
            self.state['video_b'] = b
            self.state['composite_mode'] = mode
        elif cmd == 'video_status':
            a, b = args.split()
            self.state['video_a'] = a
            self.state['video_b'] = b
        elif cmd == 'stream_status':
            self.state['stream_status'] = args


async def connect_voctomix(app):
    """Connect to voctomix, find out what's there, start the preview clients"""
    config = app['config']
    voctomix = Voctomix(
        host=config.host,
        presets=config.presets,
        broadcaster=app['broadcaster'],
        gst_pipelines=app['gst']['pipelines'])
    await voctomix.connect(reconnect_on_error=True)
    app['voctomix'] = voctomix


async def disconnect_voctomix(app):
    """Stop any running preview tasks"""
    await app['voctomix'].disconnect()
