#!/usr/bin/python3
import argparse
import logging

from aiohttp import ClientSession, web
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import generate_token

CLIENT_ID = FIXME
CLIENT_SECRET = FIXME
LOGIN_URL = 'http://127.0.0.1:8080/login'
LOGIN_COMPLETE_URL = 'http://127.0.0.1:8080/login/complete'

log = logging.getLogger('voctoweb')
routes = web.RouteTableDef()


@routes.get('/')
async def root(request):
    return web.Response(text="Hello, {}".format(request['session']['username']))


@routes.get('/login')
async def login(request):
    client = WebApplicationClient(CLIENT_ID)
    state = generate_token()
    dest = client.prepare_request_uri(
        'https://salsa.debian.org/oauth/authorize', state=state,
        scope='openid', redirect_uri=LOGIN_COMPLETE_URL)
    response = web.Response(status=302, headers={'Location': dest})
    response.set_cookie('oauth2-state', state, httponly=True)
    return response


@routes.get('/login/complete')
async def login_complete(request):
    state = request.cookies['oauth2-state']
    client = WebApplicationClient(CLIENT_ID)
    result = client.parse_request_uri_response(str(request.url), state)
    code = result['code']
    async with ClientSession() as session:
        r = await session.post('https://salsa.debian.org/oauth/token', data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': LOGIN_COMPLETE_URL,
            'grant_type': 'authorization_code',
        })
        if not r.status == 200:
            raise Exception('Failed to retrieve OAuth2 token')
        token = await r.json()

        auth_headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
        r = await session.get('https://salsa.debian.org/oauth/userinfo',
                              headers=auth_headers)
        if not r.status == 200:
            raise Exception('Failed to retrieve UserInfo')
        userinfo = await r.json()

    session = request['session']
    session['userinfo'] = userinfo
    salsa_username = userinfo['nickname']
    session['username'] = salsa_username

    next_url = request.cookies.get('next', '/')
    response = web.Response(status=302, headers={'Location': next_url})
    response.del_cookie('next')
    response.del_cookie('oauth2-state')
    return response


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


@web.middleware
async def auth_middleware(request, handler):
    """Require login to all URLs except /login.*"""
    if not request.path.startswith('/login'):
        if 'username' not in request['session']:
            response = web.Response(status=302, headers={'Location': LOGIN_URL})
            response.set_cookie('next', request.path, httponly=True)
            return response
    return await handler(request)


async def app_factory():
    app = web.Application(middlewares=[session_middleware, auth_middleware])
    app.add_routes(routes)
    app['sessions'] = {}
    return app


def main():
    p = argparse.ArgumentParser('Voctoweb API')
    p.add_argument('-v', '--verbose', action='store_true',
                   help='Increase verbosity')
    args = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    app = app_factory()
    web.run_app(app)


if __name__ == '__main__':
    main()
