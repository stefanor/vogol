from aiohttp import web

from vogol.auth import get_auth_routes
from vogol.auth.middleware import auth_middleware, session_middleware
from vogol.gst import start_glib, stop_glib, stop_gst_pipelines
from vogol.playback import initialize_player, stop_player
from vogol.routes import routes
from vogol.voctomix import connect_voctomix, disconnect_voctomix
from vogol.broadcaster import WSBroadcaster


async def app_factory(config):
    middlewares = [session_middleware]
    if config.auth:
        middlewares.append(auth_middleware)
    app = web.Application(middlewares=middlewares)
    app.add_routes(routes)
    app.add_routes(get_auth_routes(config.auth))
    app['sessions'] = {}
    app['config'] = config
    app['broadcaster'] = WSBroadcaster()
    app.on_startup.append(start_glib)
    app.on_startup.append(connect_voctomix)
    app.on_startup.append(initialize_player)
    app.on_cleanup.append(stop_player)
    app.on_cleanup.append(disconnect_voctomix)
    app.on_cleanup.append(stop_gst_pipelines)
    app.on_cleanup.append(stop_glib)
    return app
