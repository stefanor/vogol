import functools
import logging

from aiohttp import ClientSession, hdrs, web
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import generate_token


log = logging.getLogger(__name__)
auth_routes = web.RouteTableDef()


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


@auth_routes.get('/login')
async def login(request):
    config = request.app['config']
    redirect_uri = f'{config.server_url}/login/complete'
    client = WebApplicationClient(config.auth.client_id)
    state = generate_token()
    dest = client.prepare_request_uri(
        f'{config.auth.url}/oauth/authorize', state=state,
        scope='openid', redirect_uri=redirect_uri)
    response = web.Response(status=302, headers={hdrs.LOCATION: dest})
    response.set_cookie('oauth2-state', state, httponly=True)
    return response


@auth_routes.get('/login/complete')
async def login_complete(request):
    config = request.app['config']
    redirect_uri = f'{config.server_url}/login/complete'
    state = request.cookies['oauth2-state']
    client = WebApplicationClient(config.auth.client_id)
    result = client.parse_request_uri_response(
        f'{config.server_url}{request.path_qs}', state)
    code = result['code']
    async with ClientSession() as session:
        r = await session.post(f'{config.auth.url}/oauth/token', data={
            'client_id': config.auth.client_id,
            'client_secret': config.auth.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
        if not r.status == 200:
            raise Exception('Failed to retrieve OAuth2 token')
        token = await r.json()

        auth_headers = {hdrs.AUTHORIZATION: f'Bearer {token["access_token"]}'}
        r = await session.get(f'{config.auth.url}/oauth/userinfo',
                              headers=auth_headers)
        if not r.status == 200:
            raise Exception('Failed to retrieve UserInfo')
        userinfo = await r.json()

    if config.auth.group and config.auth.group not in userinfo['groups']:
        raise web.HTTPForbidden(
            reason=f'Access Denied. Not a member of {config.auth.group}.')

    session = request['session']
    session['userinfo'] = userinfo
    gitlab_username = userinfo['nickname']
    session['username'] = gitlab_username
    log.info('Login: %s', gitlab_username)

    response = web.Response(status=302, headers={hdrs.LOCATION: '/'})
    response.del_cookie('oauth2-state')
    return response
