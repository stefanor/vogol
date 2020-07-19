from aiohttp import web
from jinja2 import Environment, FileSystemLoader, select_autoescape

from voctoweb.auth import auth_middleware, session_middleware
from voctoweb.routes import routes
from voctoweb.voctomix import connect_voctomix
from voctoweb.previews import stop_polling_previews


async def app_factory(config):
    middlewares = [session_middleware]
    if config.getboolean('require_salsa_auth'):
        middlewares.append(auth_middleware)
    app = web.Application(middlewares=middlewares)
    app.add_routes(routes)
    app['sessions'] = {}
    app['config'] = config
    app['jinja_env'] = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )
    app.on_startup.append(connect_voctomix)
    app.on_cleanup.append(stop_polling_previews)
    return app
