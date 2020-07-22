import logging
from asyncio import wait_for

from aiohttp import hdrs, web

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


@routes.get('/{component:(js|css)}/{filename:[a-z0-9.-]+}')
async def static(request):
    component = request.match_info['component']
    filename = request.match_info['filename']
    return web.FileResponse(f'frontend/dist/{component}/{filename}')


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
        headers={hdrs.CACHE_CONTROL: 'no-cache'},
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
        headers={hdrs.CACHE_CONTROL: 'no-cache'},
    )
