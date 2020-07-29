import logging
from asyncio import gather, sleep, wait_for
from threading import Thread

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import GLib, Gst, GstPbutils
Gst.init(None)
GstPbutils.pb_utils_init()


log = logging.getLogger(__name__)


async def start_glib(app):
    """Start a GLib main thread"""
    loop = GLib.MainLoop()
    app['gst'] = {
        'mainloop': loop,
        'pipelines': {},
    }
    thread = Thread(target=loop.run)
    thread.start()


async def stop_glib(app):
    """Shut down the GLib main thread"""
    app['gst']['mainloop'].quit()


async def stop_pipeline(pipeline):
    """Stop a pipeline"""
    pipeline.set_state(Gst.State.NULL)
    try:
        await wait_for(wait_for_pipeline_to_stop(pipeline), timeout=1)
    except TimeoutError:
        pass


async def wait_for_pipeline_to_stop(pipeline):
    """Wait for a pipeline to reach NULL state"""
    while True:
        pipeline_state = pipeline.get_state(Gst.CLOCK_TIME_NONE)
        if pipeline_state.state == Gst.State.NULL:
            return
        await sleep(0.01)


async def stop_pipelines(pipelines):
    """Stop all of the specified pipelines"""
    await gather(*(stop_pipeline(pipeline) for pipeline in pipelines))


async def stop_gst_pipelines(app):
    """Gracefully shut down any running pipelines"""
    await stop_pipelines(app['gst']['pipelines'].values())
    app['gst']['pipelines'] = {}
