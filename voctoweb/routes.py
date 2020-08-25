import logging
from asyncio import wait_for

from aiohttp import WSMsgType, hdrs, web

from voctoweb.auth import require_login


log = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.get('/')
async def root(request):
    return web.FileResponse('frontend/dist/index.html', headers={
        hdrs.CONTENT_TYPE: 'text/html; charset=utf-8'})


@routes.get('/favicon.ico')
async def favicon(request):
    return web.FileResponse('frontend/dist/favicon.ico', headers={
        hdrs.CONTENT_TYPE: 'image/vnd.microsoft.icon'})


@routes.get('/{component:(img|js|css)}/{filename:[a-z0-9.-]+}')
async def static(request):
    component = request.match_info['component']
    filename = request.match_info['filename']
    return web.FileResponse(f'frontend/dist/{component}/{filename}')


@routes.get('/ws')
@require_login
async def websocket_handler(request):
    app = request.app
    config = app['config']
    broadcaster = app['broadcaster']
    player = request.app['player']
    voctomix = request.app['voctomix']
    username = request['session'].get('username', 'anon')

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    wsid = broadcaster.add_ws(ws, username)
    log.info('WebSocket connection %i (%s) opened', wsid, username)

    await ws.send_json({
        'type': 'config',
        'config': {
            'room_name': config.room_name,
            'username': username,
            'video_only_sources': config.video_only_sources,
        },
    })
    await ws.send_json({
        'type': 'voctomix_state',
        'state': voctomix.state,
    })
    await ws.send_json({
        'type': 'player_state',
        'state': player.state,
    })
    await ws.send_json({
        'type': 'player_files',
        'files': player.list_files(),
    })

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                body = msg.json()
                log.info('WS message from %i (%s): %r', wsid, username, body)
                type_ = body['type']
                action = body['action']
                broadcaster.broadcast({
                    'type': 'user_action',
                    'user_action': {
                        'username': username,
                        'type': type_,
                        'action': action,
                    },
                })
                r = None
                if type_ == 'voctomix':
                    r = await wait_for(voctomix.action(**action), timeout=1)
                elif type_ == 'player':
                    r = await wait_for(player.action(**action), timeout=1)
                else:
                    log.error('Unknown WS message %r from %i (%s)',
                              body, wsid, username)
                if r:
                    await ws.send_json(r)
            elif msg.type == WSMsgType.ERROR:
                log.error('WebSocket closed with %s', ws.exception())
            else:
                log.error('Unknown WS message %r from %i (%s)',
                          body, wsid, username)
    finally:
        log.info('WebSocket connection %i (%s) closed', wsid, username)
        broadcaster.remove_ws(username, wsid)
        return ws
