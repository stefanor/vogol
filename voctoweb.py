#!/usr/bin/python3
import argparse
import configparser
import logging
import json
from asyncio import (
    create_subprocess_exec, create_task, open_connection, sleep, subprocess,
    wait_for)

from aiohttp import ClientSession, web
from jinja2 import Template
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import generate_token

INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>VoctoWeb.py</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <style>
        img.room {
            width: 320px;
            height: 180px;
        }
        img.source {
            display: block;
            width: 240px;
            height: 135px;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>VoctoWeb</h1>
        <div class="row">
            <div class="card">
                <div class="card-header">Mixed Output</div>
                <div class="card-body">
                    <img class="preview room" id="loop" data-source="room">
                </div>
            </div>
            <div class="card">
                <div class="card-header">Stream</div>
                <div class="card-body">
                    <div id="stream-status"></div>
                    <button class="btn btn-success" data-action="stream_live">Go Live</button>
                    <button class="btn btn-danger" data-action="stream_blank">Blank</button>
                    <br>
                    <button class="btn btn-secondary" data-action="cut">Cut</button>
                </div>
            </div>
            <div class="card">
                <div class="card-header">Layout</div>
                <div class="card-body">
                    <div id="composite-mode"></div>
                    <br>
                    <button class="btn btn-secondary" data-action="set_composite_mode" data-mode="fullscreen">Fullscreen</button>
                    <br>
                    <button class="btn btn-secondary" data-action="set_composite_mode" data-mode="side_by_side_equal">Side by Side</button>
                    <br>
                    <button class="btn btn-secondary" data-action="set_composite_mode" data-mode="side_by_side_preview">Side by Side Preview</button>
                    <br>
                    <button class="btn btn-secondary" data-action="set_composite_mode" data-mode="picture_in_picture">Picture in Picture</button>
                </div>
            </div>
        </div>
        <div class="row">
            {% for source in sources %}
                <div class="card">
                    <div class="card-header" id="header-{{ source }}">{{ source|title }}</div>
                    <div class="card-body">
                        <img class="preview source" id="loop" data-source="{{source}}">
                        <button class="btn btn-primary" data-action="fullscreen" data-source="{{source}}">Fullscreen</button>
                        <button class="btn btn-warning" data-action="set_a" data-source="{{source}}">A</button>
                        <button class="btn btn-info" data-action="set_b" data-source="{{source}}">B</button>
                    </div>
                </div>
            {% endfor %}
        </div>
        {% if session.username %}
            <div>Logged in as {{ session.username }}.</div>
        {% endif %}
        <div>Last updated: <span id="last-update"></span></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
    <script src="/voctoweb.js"></script>
</body>
</html>
"""

JS = """
'use strict';
function updatePreview(img) {
    let source = img.dataset.source;
    let url = '/preview/' + source;
    fetch(url, {
        credentials: 'same-origin',
        redirect: 'manual',
    }).then(response => {
        if (response.type == 'opaqueredirect') {
            console.log('Preview 302ed. Presumably logged out. Reloading');
            location.reload();
        }
        if (!response.ok) {
            throw new Error('Failed to get preview');
        }
        return response.blob();
    }).then(response => {
        if (response) {
            let objectURL = URL.createObjectURL(response);
            img.src = objectURL;
            updateTimestamp();
        }
    }).catch(error => {
        // FIXME
        //console.error('Failed to fetch', source);
        //img.src = URL.createObjectURL('');
    });
}

function updateTimestamp() {
    let last_updated = document.getElementById('last-update');
    last_updated.innerHTML = new Date();
}

// Handle an action click
function actionButton(event) {
    let button = event.target;
    fetch('/action', {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(button.dataset),
    })
    .then(response => response.json())
    .then(data => {
        receivedState(data);
    });
}

// Request state from Voctomix
function updateState() {
    fetch('/state', {
        credentials: 'same-origin',
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        receivedState(data);
    });
}

// Received state from Voctomix
function receivedState(state) {
    setCurrentVideo(state.video_a, 'a');
    setCurrentVideo(state.video_b, 'b');
    let composite_mode = document.getElementById('composite-mode');
    composite_mode.innerHTML = state.composite_mode;
    let stream_status = document.getElementById('stream-status');
    stream_status.innerHTML = state.stream_status;
}

// Put the A / B label on the right source
function setCurrentVideo(source, slot) {
    let tag = document.getElementById('video-' + slot);
    if (tag) {
        if (tag.dataset.source == source) {
            return;
        } else {
            tag.remove();
        }
    }
    let parent = document.getElementById('header-' + source);
    var badge = document.createElement('div');
    badge.id = 'video-' + slot;
    if (slot == 'a') {
        badge.className = 'badge badge-primary';
    } else {
        badge.className = 'badge badge-secondary';
    }
    badge.dataset.source = source;
    badge.appendChild(document.createTextNode(slot.toUpperCase()));
    parent.appendChild(badge);
}

let previews = document.getElementsByClassName('preview');
for (let preview of previews) {
    setInterval(updatePreview, 2000, preview);
    setTimeout(updatePreview, 0, preview);
}

let buttons = document.getElementsByTagName('button');
for (let button of buttons) {
    button.onclick = actionButton;
}
setInterval(updateState, 5000);
"""

log = logging.getLogger('voctoweb')
routes = web.RouteTableDef()


@routes.get('/')
async def root(request):
    session = request['session']
    template = Template(INDEX)
    body = template.render(
        session=session,
        sources=request.app['voctomix'].sources,
    )
    return web.Response(body=body, content_type='text/html', charset='utf-8')


@routes.get('/voctoweb.js')
async def js(request):
    return web.Response(
        body=JS, content_type='text/javascript', charset='utf-8')


@routes.get('/preview/{source:[a-z0-9-]+}')
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
async def action(request):
    data = await request.json()
    voctomix = request.app['voctomix']

    await wait_for(voctomix.action(**data), timeout=1)
    return web.json_response(voctomix.state)


@routes.get('/state')
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
            response = web.Response(
                status=302, headers={'Location': '/login'})
            response.set_cookie('next', request.path, httponly=True)
            return response
    return await handler(request)


class VoctomixControl:
    async def connect(self, host):
        log.info('Connecting to voctomix control')
        self.reader, self.writer = await open_connection(host, 9999)
        self.state = {}
        await self.send('get_config')
        await self.send('get_stream_status')
        await self.send('get_composite_mode_and_video_status')

    async def send(self, *command):
        """Send a command to voctomix"""
        cmd = ' '.join(command)
        self.writer.write(cmd.encode('utf-8'))
        self.writer.write(b'\n')
        await self.writer.drain()
        last_responses = {
            'get_config': 'server_config',
            'get_composite_mode_and_video_status':
                'composite_mode_and_video_status',
            'get_stream_status': 'stream_status',
            'message': 'message',
            'set_composite_mode': 'composite_mode_and_video_status',
            'set_stream_blank': 'stream_status',
            'set_stream_live': 'stream_status',
            'set_video_a': 'video_status',
            'set_video_b': 'video_status',
        }
        return await self.expect(last_responses[command[0]])

    async def expect(self, command):
        """Wait for a particular response from voctomix"""
        while True:
            line = await self.reader.readline()
            line = line.decode('utf-8').strip()
            cmd, args = line.split(None, 1)
            self.update_state(cmd, args)
            if cmd == command:
                return args

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
        elif action == 'cut':
            await self.send('message', 'cut')
        else:
            raise Exception(f'Unknown action: {action}')

    def update_state(self, cmd, args):
        """Update our view of Voctomix's state, based on a received message"""
        if cmd == 'server_config':
            self.config = json.loads(args)
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
        await self.reader.wait_closed()
        await self.writer.wait_closed()

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
