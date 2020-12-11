import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Preset:
    audio_solo: List[str]
    composite_mode: str
    name: str
    video_a: str
    video_b: Optional[str]


class AuthConfig:
    pass


@dataclass
class Config:
    host: str
    auth: AuthConfig
    presets: Dict[str, Preset]
    room_name: str
    server_url: str
    video_only_sources: List[str]
    recordings: Path


@dataclass
class AuthGitLab(AuthConfig):
    type = 'gitlab'
    client_id: str
    client_secret: str
    group: Optional[List[str]]
    name: str
    url: str


def parse_config_list(config, key):
    text = config.get(key)
    return [item.strip() for item in text.split(',') if item.strip()]


def parse_config(config_file):
    cfgp = configparser.ConfigParser()
    cfgp.read(config_file)

    auth = None
    presets = {}
    for section_name in cfgp.sections():
        section = cfgp[section_name]
        if section_name == 'auth:gitlab':
            auth = AuthGitLab(
                client_id=section.get('client_id'),
                client_secret=section.get('client_secret'),
                group=section.get('group'),
                name=section.get('name'),
                url=section.get('url'),
            )
        if section_name.startswith('preset:'):
            id_ = section_name.split(':', 1)[1]
            presets[id_] = Preset(
                audio_solo=parse_config_list(section, 'audio_solo'),
                composite_mode=section['composite_mode'],
                name=section['name'],
                video_a=section['video_a'],
                video_b=section.get('video_b'),
            )

    vogol = cfgp['vogol']
    config = Config(
        host=vogol['host'],
        auth=auth,
        presets=presets,
        recordings=Path(vogol['recordings']),
        room_name=vogol['room_name'],
        server_url=vogol['server_url'],
        video_only_sources=parse_config_list(vogol, 'video_only_sources'),
    )
    return config
