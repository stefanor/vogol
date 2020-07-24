import logging
from asyncio import get_running_loop, run_coroutine_threadsafe, sleep
from threading import Thread

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
Gst.init(None)


log = logging.getLogger(__name__)


async def start_glib(app):
    """Start a GLib main thread"""
    app['glib_mainloop'] = loop = GLib.MainLoop()
    app['gst_pipelines'] = {}
    thread = Thread(target=loop.run)
    thread.start()


async def stop_glib(app):
    """Shut down the GLib main thread"""
    app['glib_mainloop'].quit()


async def stop_gst_pipelines(app):
    """Gracefully shut down any running preview pipelines"""
    for pipeline in app['gst_pipelines'].values():
        pipeline.set_state(Gst.State.NULL)
    app['gst_pipelines'] = {}


async def monitor_stream(app, source, port):
    """Start a pipeline to generate preview images from source, every second"""
    host = app['config']['host']
    log.info('Attempting to start preview pipeline for %s polling %s:%s',
             source, host, port)

    pipeline = Gst.parse_launch("""
    tcpclientsrc name=src
    ! matroskademux
    ! videoconvert
    ! videorate max-rate=1
    ! videoscale
    ! video/x-raw, width=320, height=180
    ! jpegenc
    ! appsink name=sink emit-signals=true drop=true max-buffers=1
    """)

    src = pipeline.get_by_name('src')
    src.set_property('host', host)
    src.set_property('port', port)

    sink = pipeline.get_by_name('sink')
    sink.connect('new-sample', new_sample, source, app['previews'])

    loop = get_running_loop()
    bus = pipeline.bus
    bus.add_signal_watch()
    bus.connect('message', gst_message, app, source, port, loop)

    pipeline.set_state(Gst.State.PLAYING)
    log.info('Started preview pipeline for %s', source)
    app['gst_pipelines'][source] = pipeline


async def restart_stream(app, source, port):
    """Shut down any existing stream, wait a few seconds, and restart it"""
    pipeline = app['gst_pipelines'].pop(source, None)
    if pipeline:
        pipeline.set_state(Gst.State.NULL)

    await sleep(5)

    await monitor_stream(app, source, port)


# Asyncio thread, above
#######################
# GLib thread, below


def gst_message(bus, message, app, source, port, loop):
    """GLib thread callback: GstBus message

    Restart the pipeline if it has failed / ended
    """
    if message.type in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
        log.error('Received %s from %s preview pipeline', message.type, source)
        run_coroutine_threadsafe(restart_stream(app, source, port), loop)


def new_sample(sink, source, previews):
    """GLib thread callback: GstAppSink has a new frame ready

    Save it in the previews dict.
    """

    sample = sink.emit('pull-sample')
    if not isinstance(sample, Gst.Sample):
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()
    status, mapinfo = buf.map(Gst.MapFlags.READ)
    if not status:
        return Gst.FlowReturn.ERROR

    previews[source] = mapinfo.data

    return Gst.FlowReturn.OK
