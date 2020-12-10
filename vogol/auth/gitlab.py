import logging

from aiohttp import ClientSession, hdrs, web

from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import generate_token

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/login')
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


@routes.get('/login/complete')
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
