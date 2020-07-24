import logging
from asyncio import get_running_loop, sleep

from voctoweb.gst import Gst


log = logging.getLogger(__name__)


async def preview_task(app, source, port):
    """Start and monitor a preview pipeline"""
    while True:
        await preview_client(app, source, port)
        await sleep(5)


async def preview_client(app, source, port):
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

    completion = get_running_loop().create_future()
    bus = pipeline.bus
    bus.add_signal_watch()
    bus.connect('message', gst_message, completion, source)

    pipeline.set_state(Gst.State.PLAYING)
    log.info('Started preview pipeline for %s', source)
    app['gst']['pipelines'][source] = pipeline

    await completion
    pipeline.set_state(Gst.State.NULL)


def stream_ended(completion, result):
    """Report the stream as ended, unless already done"""
    if not completion.done():
        completion.set_result(result)


# Asyncio thread, above
#######################
# GLib thread, below


def gst_message(bus, message, completion, source):
    """GLib thread callback: GstBus message

    Report stream completion, if the message is fatal
    """
    type_ = message.type
    if type_ in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
        log.error('Received %s from %s preview pipeline', type_, source)
        loop = completion.get_loop()
        loop.call_soon_threadsafe(stream_ended, completion, type_)


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
