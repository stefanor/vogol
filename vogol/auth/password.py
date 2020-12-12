import logging

from aiohttp import hdrs, web
from passlib.apache import HtpasswdFile

log = logging.getLogger(__name__)


routes = web.RouteTableDef()


@routes.post('/login')
async def login(request):
    config = request.app['config']
    data = await request.post()
    username = data.get('username', '')
    password = data.get('password', '')

    ht = HtpasswdFile(config.auth.htpassdb)
    # TODO: Move auth into a niced ProcessPoolExecutor
    if not ht.check_password(username, password):
        raise web.HTTPForbidden(reason='credentials invalid')

    session = request['session']
    session['username'] = username
    log.info('Login: %s', username)
    return web.Response(status=302, headers={hdrs.LOCATION: '/'})


def get_auth_required_dict(auth_config):
    return {}
