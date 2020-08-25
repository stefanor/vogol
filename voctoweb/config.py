import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Config:
    host: str
    require_salsa_auth: bool
    room_name: str
    salsa_client_id: Optional[str]
    salsa_client_secret: Optional[str]
    salsa_group: Optional[List[str]]
    server_url: str
    video_only_sources: List[str]
    recordings: Path


def parse_config_list(config, key):
    text = config.get(key)
    return [item.strip() for item in text.split(',') if item.strip()]


def parse_config(config_file):
    cfgp = configparser.ConfigParser()
    cfgp.read(config_file)
    voctoweb = cfgp['voctoweb']
    config = Config(
        host=voctoweb['host'],
        require_salsa_auth=voctoweb.getboolean('require_salsa_auth'),
        recordings=Path(voctoweb['recordings']),
        room_name=voctoweb['room_name'],
        salsa_client_id=voctoweb.get('salsa_client_id'),
        salsa_client_secret=voctoweb.get('salsa_client_secret'),
        salsa_group=voctoweb.get('salsa_group'),
        server_url=voctoweb['server_url'],
        video_only_sources=parse_config_list(voctoweb, 'video_only_sources'),
    )
    return config
