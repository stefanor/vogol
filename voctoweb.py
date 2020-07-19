#!/usr/bin/python3
import argparse
import configparser
import functools
import logging
import json
from asyncio import (
    CancelledError, create_subprocess_exec, create_task, get_running_loop,
    open_connection, sleep, subprocess, wait_for)
from collections import defaultdict

from aiohttp import ClientSession, web
from jinja2 import Environment, FileSystemLoader, select_autoescape
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import generate_token


log = logging.getLogger('voctoweb')
routes = web.RouteTableDef()


def require_login(func):
    """Decorator to mark a route as requiring login"""
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    wrapped.require_login = True
    return wrapped


@routes.get('/')
async def root(request):
    session = request['session']
    template = request.app['jinja_env'].get_template('index.html.j2')
    if request.app['config'].getboolean('require_salsa_auth'):
        logged_in = 'username' in session
    else:
        logged_in = True
    body = template.render(
        session=session,
        logged_in=logged_in,
        sources=request.app['voctomix'].sources,
    )
    return web.Response(body=body, content_type='text/html', charset='utf-8')


@routes.get('/static/{filename:[a-z0-9.-]+}')
async def static(request):
    filename = request.match_info['filename']
    return web.FileResponse(f'static/{filename}')


@routes.get('/preview/{source:[a-z0-9-]+}')
@require_login
async def preview_image(request):
    source = request.match_info['source']
    preview = request.app['previews'].get(source)
    if not preview:
        raise web.HTTPNotFound()
    return web.Response(
        body=preview,
        content_type='image/jpeg',
        headers={'Cache-Control': 'no-cache'},
    )


@routes.post('/action')
@require_login
async def action(request):
    data = await request.json()
    voctomix = request.app['voctomix']
    username = request['session'].get('username', 'anon')
    log.info('Action by %s: %r', username, data)

    await wait_for(voctomix.action(**data), timeout=1)
    return web.json_response(voctomix.state)


@routes.get('/state')
@require_login
async def state(request):
    voctomix = request.app['voctomix']
    return web.json_response(
        voctomix.state,
        headers={'Cache-Control': 'no-cache'},
    )


@routes.get('/login')
async def login(request):
    config = request.app['config']
    redirect_uri = f'{config["server_url"]}/login/complete'
    client = WebApplicationClient(config['salsa_client_id'])
    state = generate_token()
    dest = client.prepare_request_uri(
        'https://salsa.debian.org/oauth/authorize', state=state,
        scope='openid', redirect_uri=redirect_uri)
    response = web.Response(status=302, headers={'Location': dest})
    response.set_cookie('oauth2-state', state, httponly=True)
    return response


@routes.get('/login/complete')
async def login_complete(request):
    config = request.app['config']
    redirect_uri = f'{config["server_url"]}/login/complete'
    state = request.cookies['oauth2-state']
    client = WebApplicationClient(config['salsa_client_id'])
    result = client.parse_request_uri_response(
        f'{config["server_url"]}{request.path_qs}', state)
    code = result['code']
    async with ClientSession() as session:
        r = await session.post('https://salsa.debian.org/oauth/token', data={
            'client_id': config['salsa_client_id'],
            'client_secret': config['salsa_client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
        if not r.status == 200:
            raise Exception('Failed to retrieve OAuth2 token')
        token = await r.json()

        auth_headers = {'Authorization': f'Bearer {token["access_token"]}'}
        r = await session.get('https://salsa.debian.org/oauth/userinfo',
                              headers=auth_headers)
        if not r.status == 200:
            raise Exception('Failed to retrieve UserInfo')
        userinfo = await r.json()

    session = request['session']
    session['userinfo'] = userinfo
    salsa_username = userinfo['nickname']
    session['username'] = salsa_username
    log.info('Login: %s', salsa_username)

    response = web.Response(status=302, headers={'Location': '/'})
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
    if getattr(handler, 'require_login', False):
        if 'username' not in request['session']:
            raise web.HTTPForbidden()
    return await handler(request)


class VoctomixControl:
    async def connect(self, host):
        log.info('Connecting to voctomix control')
        self.reader, self.writer = await open_connection(host, 9999)
        self.loop = get_running_loop()
        self.state = {}
        self.response_futures = defaultdict(list)
        create_task(self.reader_task())
        # Initialize our state
        await self.send('get_config')
        await self.send('get_audio')
        await self.send('get_stream_status')
        await self.send('get_composite_mode_and_video_status')

    async def reader_task(self):
        """Follow events from the core

        They can arrive at any time.
        If anyone is waiting for one of them, notify them.
        """
        while True:
            try:
                line = await self.reader.readline()
            except CancelledError:
                return
            line = line.decode('utf-8').strip()
            cmd, args = line.split(None, 1)
            self.update_state(cmd, args)
            futures = self.response_futures[cmd]
            while futures:
                future = futures.pop(0)
                future.set_result(args)

    async def send(self, *command):
        """Send a command to voctomix"""
        cmd = ' '.join(command)
        self.writer.write(cmd.encode('utf-8'))
        self.writer.write(b'\n')
        await self.writer.drain()
        last_responses = {
            'get_audio': 'audio_status',
            'get_config': 'server_config',
            'get_composite_mode_and_video_status':
                'composite_mode_and_video_status',
            'get_stream_status': 'stream_status',
            'message': 'message',
            'set_audio_volume': 'audio_status',
            'set_composite_mode': 'composite_mode_and_video_status',
            'set_stream_blank': 'stream_status',
            'set_stream_live': 'stream_status',
            'set_stream_loop': 'stream_status',
            'set_video_a': 'video_status',
            'set_video_b': 'video_status',
        }
        return await self.expect(last_responses[command[0]])

    async def expect(self, command):
        """Wait for a particular response from voctomix"""
        future = self.loop.create_future()
        self.response_futures[command].append(future)
        return await future

    async def action(self, action, source=None, mode=None):
        """Fire an action requested by the client"""
        if action == 'fullscreen':
            await self.send('set_composite_mode', 'fullscreen')
            await self.send('set_video_a', source)
        elif action == 'set_composite_mode':
            await self.send('set_composite_mode', mode)
        elif action =='set_a':
            await self.send('set_video_a', source)
        elif action =='set_b':
            await self.send('set_video_b', source)
        elif action == 'stream_live':
            await self.send('set_stream_live')
        elif action == 'stream_blank':
            await self.send('set_stream_blank', 'nostream')
        elif action == 'stream_loop':
            await self.send('set_stream_blank', 'loop')
        elif action == 'mute':
            await self.send('set_audio_volume', source, '0')
        elif action == 'unmute':
            await self.send('set_audio_volume', source, '1')
        elif action == 'cut':
            await self.send('message', 'cut')
        else:
            raise Exception(f'Unknown action: {action}')

    def update_state(self, cmd, args):
        """Update our view of Voctomix's state, based on a received message"""
        if cmd == 'server_config':
            self.config = json.loads(args)
        elif cmd == 'audio_status':
            self.state['audio'] = json.loads(args)
        elif cmd == 'composite_mode_and_video_status':
            mode, a, b = args.split()
            self.state['video_a'] = a
            self.state['video_b'] = b
            self.state['composite_mode'] = mode
        elif cmd == 'video_status':
            a, b = args.split()
            self.state['video_a'] = a
            self.state['video_b'] = b
        elif cmd == 'stream_status':
            self.state['stream_status'] = args

    async def close(self):
        self.reader.close()
        self.writer.close()

    @property
    def sources(self):
        return self.config['mix']['sources'].split(',')


async def connect_voctomix(app):
    config = app['config']
    voctomix = app['voctomix'] = VoctomixControl()
    await voctomix.connect(config['host'])
    ports = [(source, i + 13000) for i, source in enumerate(voctomix.sources)]
    ports.append(('room', 11000))
    app['preview_pollers'] = {
        source: create_task(poll_previews(app, source, port))
        for source, port in ports}
    app['previews'] = {}


async def stop_polling_previews(app):
    for task in app['preview_pollers'].values():
        task.cancel()


async def poll_previews(app, source, port):
    """Update previews for source, every second"""
    host = app['config']['host']
    while True:
        try:
            preview = preview_source(host, source, port)
            app['previews'][source] = await wait_for(preview, timeout=10)
        except CancelledError:
            return
        except Exception:
            log.exception('Exception previewing source %s', source)
        await sleep(1)


async def preview_source(host, source, port):
    """Generate and return a single preview image"""
    log.debug('Previewing %s', source)
    proc = await create_subprocess_exec(
        'ffmpeg', '-v', 'quiet', '-y',
        '-i', f'tcp://{host}:{port}?timeout=1000000',
        '-map', '0:v', '-an',
        '-s', '320x180',
        '-q', '5',
        '-vframes', '1',
        '-f', 'singlejpeg',
        '-',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(f'ffmpeg exited {proc.returncode}: {stderr}')
    return stdout


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


def main():
    p = argparse.ArgumentParser('Voctoweb API')
    p.add_argument('-v', '--verbose', action='store_true',
                   help='Increase verbosity')
    p.add_argument('-c', '--config',
                   default='/etc/voctomix/voctoweb.ini',
                   help='Configuration file')
    args = p.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    app = app_factory(config['voctoweb'])
    web.run_app(app)


if __name__ == '__main__':
    main()
