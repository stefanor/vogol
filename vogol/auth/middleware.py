import functools

from aiohttp import web
from oauthlib.common import generate_token


def require_login(func):
    """Decorator to mark a route as requiring login"""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    wrapped.require_login = True
    return wrapped


@web.middleware
async def auth_middleware(request, handler):
    if getattr(handler, 'require_login', False):
        if 'username' not in request['session']:
            raise web.HTTPForbidden()
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
