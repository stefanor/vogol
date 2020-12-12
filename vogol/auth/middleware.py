import functools
import json

from aiohttp import web
from oauthlib.common import generate_token

from vogol.auth import get_auth_required_dict


def require_login(func):
    """Decorator to mark a route as requiring login"""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    wrapped.require_login = True
    return wrapped


@web.middleware
async def auth_middleware(request, handler):
    config = request.app['config']
    if getattr(handler, 'require_login', False):
        if 'username' not in request['session']:
            auth_dict = get_auth_required_dict(config.auth)
            raise web.HTTPForbidden(
                text=json.dumps(auth_dict),
                content_type='application/json')
    return await handler(request)


@web.middleware
async def session_middleware(request, handler):
    """A simple in-memory session store"""
    sessions = request.app['sessions']
    session = {}
    sessionid = request.cookies.get('sessionid')
    if sessionid:
        session = sessions.get(sessionid, {})
    request['session'] = session

    response = await handler(request)

    if session:
        if not sessionid:
            sessionid = generate_token()
            response.set_cookie('sessionid', sessionid, httponly=True)
        sessions[sessionid] = session
    else:
        if sessionid:
            response.del_cookie('sessionid')
            sessions.pop(sessionid, None)
    return response
