import logging
from asyncio import create_task, get_running_loop, sleep
from pathlib import Path

from voctoweb.gst import Gst, GstPbutils, stop_pipeline


log = logging.getLogger(__name__)


class VideoPlayer:
    def __init__(self, base_dir, broadcaster, voctomix, source_name):
        self.base_dir = Path(base_dir)
        self.broadcaster = broadcaster
        self.voctomix = voctomix
        self.source_name = source_name

        self.file = None
        self.duration = None
        self.position = None
        self.playback = 'stopped'
        self.playback_pipeline = None
        self.playback_future = None

    def list_files(self):
        files = []
        for extension in ('mp4', 'webm', 'mkv'):
            files.extend(self.base_dir.glob(f'*.{extension}'))
        files = [str(file_.relative_to(self.base_dir)) for file_ in files]
        files.sort()
        return files

    def refresh_files(self):
        return {
            'type': 'player_files',
            'files': self.list_files(),
        }

    @property
    def state(self):
        return {
            'file': self.file,
            'duration': self.duration,
            'playback': self.playback,
            'position': self.position,
        }

    async def action(self, action=None, file=None):
        if action == 'load':
            await self.load_file(file)
        elif action == 'play':
            await self.play()
        elif action == 'stop':
            await self.stop()
        elif action == 'refresh_files':
            return self.refresh_files()
        else:
            raise Exception(f'Unkown action {action}')

    async def load_file(self, filename):
        """Load a file, determine the duration"""
        if self.playback != 'stopped':
            raise Exception(f'Can not change file while {self.playback}')

        path = self.base_dir / filename
        if not path.exists():
            raise Exception('Unknown file {filename}')

        self.file = filename
        duration = await file_duration(path)
        self.duration = format_time(duration)
        await self.broadcast_state()

    async def play(self):
        """Start playback of the selected file"""
        if self.playback != 'stopped':
            raise Exception(f'Can not start playback while {self.playback}')
        if not self.file:
            raise Exception('No file selected to play')


        path = self.base_dir / self.file
        host = self.voctomix.host
        port = self.voctomix.source_port(self.source_name)
        videocaps = self.voctomix.mix_videocaps
        audiocaps = self.voctomix.mix_audiocaps

        pipeline, future = file_play(path, host, port, videocaps, audiocaps)
        self.playback_pipeline = pipeline
        self.playback_future = future
        self.playback = 'playing'
        await self.broadcast_state()
        create_task(self.monitor_playback())

    async def stop(self):
        """Stop playback of the current file"""
        self.playback = 'stopped'
        await self.broadcast_state()
        if self.playback_future:
            set_result(self.playback_future, None)
        if self.playback_pipeline:
            await stop_pipeline(self.playback_pipeline)
            self.plyaback_pipeline = None

    async def monitor_playback(self):
        """Monitor playback, updating self.{playback,position}"""
        pipeline = self.playback_pipeline
        future = self.playback_future
        while True:
            pipeline_state = pipeline.get_state(Gst.CLOCK_TIME_NONE)
            if pipeline_state.state == Gst.State.NULL or future.done():
                await self.stop()
                break
            elif pipeline_state.state == Gst.State.PAUSED:
                self.playback = 'paused'
            elif pipeline_state.state == Gst.State.PLAYING:
                self.playback = 'playing'
                pos = pipeline.query_position(Gst.Format.TIME)
                self.position = format_time(pos.cur)
            await self.broadcast_state()
            await sleep(0.5)

    async def broadcast_state(self):
        self.broadcaster.broadcast({
            'type': 'player_state',
            'state': self.state,
        })


async def initialize_player(app):
    """Initialize the video player"""
    config = app['config']
    player = VideoPlayer(
        base_dir=config['recordings'],
        broadcaster=app['broadcaster'],
        voctomix=app['voctomix'],
        source_name='recording')
    app['player'] = player


async def stop_player(app):
    """Stop any playback"""
    await app['player'].stop()


async def file_duration(path):
    """Determine a file's duration"""
    discoverer = GstPbutils.Discoverer.new(2 * Gst.SECOND)
    discoverer.start()

    loop = get_running_loop()
    duration_future = loop.create_future()

    discoverer.connect('discovered', file_discovered, duration_future)
    discoverer.discover_uri_async(path.as_uri())
    duration = await duration_future
    discoverer.stop()
    return duration


def file_play(path, host, port, videocaps, audiocaps):
    """Start playback of path to host:port at the specified caps.

    Return the pipeline.
    """
    pipeline_str = f"""
    filesrc name=src
    ! decodebin name=demux

    demux.
    ! queue
    ! videoconvert
    ! yadif
    ! videorate
    ! videoscale
    ! {videocaps}
    ! queue
    ! mux.

    demux.
    ! queue
    ! audioconvert
    ! audioresample
    ! audiorate
    ! {audiocaps}
    ! queue
    ! mux.

    matroskamux name=mux streamable=true
    ! watchdog
    ! tcpclientsink name=sink
    """
    pipeline = Gst.parse_launch(pipeline_str)

    loop = get_running_loop()
    playback_future = loop.create_future()

    pipeline.bus.add_signal_watch()
    pipeline.bus.connect('message::eos', eos_report_none, playback_future)

    src = pipeline.get_by_name('src')
    src.set_property('location', path)

    sink = pipeline.get_by_name('sink')
    sink.set_property('host', host)
    sink.set_property('port', port)

    pipeline.set_state(Gst.State.PLAYING)
    return (pipeline, playback_future)


def set_result(future, result):
    """Complete a future, with result"""
    if future.done():
        log.error('Future is already done %r, ignoring result %r',
                  future, result)
    else:
        future.set_result(result)


def format_time(nsecs):
    """Pretty-print a gst timestamp"""
    secs = nsecs // Gst.SECOND
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return f'{hours:02}:{mins:02}:{secs:02}'


# Asyncio thread, above
#######################
# GLib thread, below


def file_discovered(discoverer, info, error, duration_future):
    """Parse a DiscovererInfo and resolve the future"""
    loop = duration_future.get_loop()
    duration = info.get_duration()
    loop.call_soon_threadsafe(set_result, duration_future, duration)


def eos_report_none(bus, message, eos_future):
    """Fires in GStreamer thread, setting eos_future to None"""
    loop = eos_future.get_loop()
    loop.call_soon_threadsafe(set_result, eos_future, None)
