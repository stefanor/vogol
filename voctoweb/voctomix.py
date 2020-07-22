import logging
import json
from asyncio import (
    CancelledError, create_task, get_running_loop, open_connection)
from collections import defaultdict

from voctoweb.previews import poll_previews

log = logging.getLogger(__name__)


class VoctomixControl:
    async def connect(self, host):
        log.info('Connecting to voctomix control')
        self.reader, self.writer = await open_connection(host, 9999)
        self.loop = get_running_loop()
        self.state = {}
        self.response_futures = defaultdict(list)
        create_task(self.reader_task())
        # Initialize our state
        await self.send('get_config')
        await self.send('get_audio')
        await self.send('get_stream_status')
        await self.send('get_composite_mode_and_video_status')

    async def reader_task(self):
        """Follow events from the core

        They can arrive at any time.
        If anyone is waiting for one of them, notify them.
        """
        while True:
            try:
                line = await self.reader.readline()
            except CancelledError:
                return
            line = line.decode('utf-8').strip()
            cmd, args = line.split(None, 1)
            self.update_state(cmd, args)
            futures = self.response_futures[cmd]
            while futures:
                future = futures.pop(0)
                future.set_result(args)

    async def send(self, *command):
        """Send a command to voctomix"""
        cmd = ' '.join(command)
        self.writer.write(cmd.encode('utf-8'))
        self.writer.write(b'\n')
        await self.writer.drain()
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
        }
        return await self.expect(last_responses[command[0]])

    async def expect(self, command):
        """Wait for a particular response from voctomix"""
        future = self.loop.create_future()
        self.response_futures[command].append(future)
        return await future

    async def action(self, action, source=None, mode=None):
        """Fire an action requested by the client"""
        if action == 'fullscreen':
            await self.send('set_composite_mode', 'fullscreen')
            await self.send('set_video_a', source)
        elif action == 'set_composite_mode':
            await self.send('set_composite_mode', mode)
        elif action =='set_a':
            await self.send('set_video_a', source)
        elif action =='set_b':
            await self.send('set_video_b', source)
        elif action == 'stream_live':
            await self.send('set_stream_live')
        elif action == 'stream_blank':
            await self.send('set_stream_blank', 'nostream')
        elif action == 'stream_loop':
            await self.send('set_stream_blank', 'loop')
        elif action == 'mute':
            await self.send('set_audio_volume', source, '0')
        elif action == 'unmute':
            await self.send('set_audio_volume', source, '1')
        elif action == 'cut':
            await self.send('message', 'cut')
        else:
            raise Exception(f'Unknown action: {action}')

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

    async def close(self):
        self.reader.close()
        self.writer.close()

    @property
    def sources(self):
        return self.state['sources']


async def connect_voctomix(app):
    """Connect to voctomix, find out what's there, start the preview pollers"""
    config = app['config']
    voctomix = app['voctomix'] = VoctomixControl()
    await voctomix.connect(config['host'])
    ports = [(source, i + 13000) for i, source in enumerate(voctomix.sources)]
    ports.append(('room', 11000))
    app['preview_pollers'] = {
        source: create_task(poll_previews(app, source, port))
        for source, port in ports}
    app['previews'] = {}
