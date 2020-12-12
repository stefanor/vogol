from importlib import import_module


from vogol.auth.routes import auth_disabled_routes


def get_auth_module(auth_config):
    """Load the configured auth module"""
    if not auth_config:
        return None
    return import_module(f'vogol.auth.{auth_config.type}')


def get_auth_required_dict(auth_config):
    """Return a dict describing the configured auth module to the frontend"""
    mod = get_auth_module(auth_config)
    if not mod:
        return {'error': 'Auth is not configured'}
    auth_required_dict = mod.get_auth_required_dict(auth_config)
    auth_required_dict.setdefault('type', auth_config.type)
    return auth_required_dict


def get_auth_routes(auth_config):
    """Load the auth routes for the configured auth module"""
    mod = get_auth_module(auth_config)
    if not mod:
        return auth_disabled_routes
    return mod.routes
