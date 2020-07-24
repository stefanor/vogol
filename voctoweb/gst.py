import logging
from threading import Thread

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
Gst.init(None)


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


async def stop_gst_pipelines(app):
    """Gracefully shut down any running pipelines"""
    for pipeline in app['gst']['pipelines'].values():
        pipeline.set_state(Gst.State.NULL)
    app['gst']['pipelines'] = {}
