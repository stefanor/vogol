from aiohttp import web


auth_disabled_routes = web.RouteTableDef()


@auth_disabled_routes.get('/login')
async def login(request):
    raise web.HTTPNotFound(reason='auth is not enabled')
