import argparse
import configparser
import logging

from aiohttp import web

from voctoweb.app import app_factory


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
