import argparse
import logging

from aiohttp import web

from voctoweb.app import app_factory
from voctoweb.config import parse_config


def main():
    p = argparse.ArgumentParser('Voctoweb API')
    p.add_argument('-v', '--verbose', action='store_true',
                   help='Increase verbosity')
    p.add_argument('-c', '--config',
                   default='/etc/voctomix/voctoweb.ini',
                   help='Configuration file')
    args = p.parse_args()

    config = parse_config(args.config)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    app = app_factory(config)
    web.run_app(app)


if __name__ == '__main__':
    main()
