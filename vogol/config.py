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


@dataclass
class Config:
    host: str
    presets: Dict[str, Preset]
    require_gitlab_auth: bool
    room_name: str
    gitlab_client_id: Optional[str]
    gitlab_client_secret: Optional[str]
    gitlab_group: Optional[List[str]]
    gitlab_url: Optional[str]
    server_url: str
    video_only_sources: List[str]
    recordings: Path


def parse_config_list(config, key):
    text = config.get(key)
    return [item.strip() for item in text.split(',') if item.strip()]


def parse_config(config_file):
    cfgp = configparser.ConfigParser()
    cfgp.read(config_file)

    presets = {}
    for section_name in cfgp.sections():
        section = cfgp[section_name]
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
        presets=presets,
        require_gitlab_auth=vogol.getboolean('require_gitlab_auth'),
        recordings=Path(vogol['recordings']),
        room_name=vogol['room_name'],
        gitlab_client_id=vogol.get('gitlab_client_id'),
        gitlab_client_secret=vogol.get('gitlab_client_secret'),
        gitlab_group=vogol.get('gitlab_group'),
        gitlab_url=vogol.get('gitlab_url'),
        server_url=vogol['server_url'],
        video_only_sources=parse_config_list(vogol, 'video_only_sources'),
    )
    return config
