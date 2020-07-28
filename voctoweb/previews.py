import logging
from asyncio import get_running_loop

from voctoweb.gst import Gst, stop_pipeline


log = logging.getLogger(__name__)


async def preview_pipeline(host, port, source, previews, gst_pipelines):
    """Start a pipeline to generate preview images from source, every second"""
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
    sink.connect('new-sample', new_sample, source, previews)

    completion = get_running_loop().create_future()
    bus = pipeline.bus
    bus.add_signal_watch()
    bus.connect('message', gst_message, completion, source)

    pipeline.set_state(Gst.State.PLAYING)
    log.info('Started preview pipeline for %s', source)
    gst_pipelines[source] = pipeline

    await completion
    await stop_pipeline(pipeline)


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
