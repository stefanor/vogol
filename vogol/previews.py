import logging
from asyncio import get_running_loop

from vogol.gst import Gst, stop_pipeline


log = logging.getLogger(__name__)


async def preview_pipeline(host, port, source, broadcaster, gst_pipelines):
    """Start a pipeline to generate preview images from source, every second"""
    log.info('Attempting to start preview pipeline for %s polling %s:%s',
             source, host, port)

    pipeline = Gst.parse_launch("""
    tcpclientsrc name=src
    ! matroskademux name=demux

    demux.
    ! queue
    ! audioconvert
    ! audio/x-raw, channels=1
    ! level interval=300000000
    ! fakesink

    demux.
    ! queue
    ! videoconvert
    ! videorate max-rate=1
    ! videoscale
    ! video/x-raw, width=320, height=180
    ! watchdog timeout=5000
    ! jpegenc name=enc
    ! appsink name=sink emit-signals=true drop=true max-buffers=1
    """)

    src = pipeline.get_by_name('src')
    src.set_property('host', host)
    src.set_property('port', port)

    sink = pipeline.get_by_name('sink')
    loop = get_running_loop()
    sink.connect('new-sample', new_sample, source, broadcaster, loop)

    completion = get_running_loop().create_future()
    bus = pipeline.bus
    bus.add_signal_watch()
    bus.connect('message', gst_message, completion, source, broadcaster)

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


def gst_message(bus, message, completion, source, broadcaster):
    """GLib thread callback: GstBus message

    Report stream completion, if the message is fatal
    """
    type_ = message.type
    loop = completion.get_loop()
    if type_ in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
        log.error('Received %s from %s preview pipeline', type_, source)
        loop.call_soon_threadsafe(stream_ended, completion, type_)
    elif type_ == Gst.MessageType.ELEMENT and message.has_name('level'):
        structure = message.get_structure()
        if structure is None:
            return
        loop.call_soon_threadsafe(
            broadcaster.broadcast, {
                'type': 'preview_audio_level',
                'source': source,
                'rms': structure.get_value('rms')[0],
                'peak': structure.get_value('peak')[0],
                'decay': structure.get_value('decay')[0],
            })


def new_sample(sink, source, broadcaster, loop):
    """GLib thread callback: GstAppSink has a new frame ready

    Broadcast it to clients.
    """

    sample = sink.emit('pull-sample')
    if not isinstance(sample, Gst.Sample):
        return Gst.FlowReturn.ERROR

    buf = sample.get_buffer()
    status, mapinfo = buf.map(Gst.MapFlags.READ)
    if not status:
        return Gst.FlowReturn.ERROR
    # Feels like there should be a better way
    jpeg = bytes(bytearray(mapinfo.data))
    buf.unmap(mapinfo)

    loop.call_soon_threadsafe(
        broadcaster.broadcast, {
            'type': 'preview',
            'source': source,
            'jpeg': jpeg,
        }
    )

    return Gst.FlowReturn.OK
