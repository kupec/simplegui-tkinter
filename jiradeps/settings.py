import asyncio
import json
from os import mkdir
from pathlib import Path

import aiofiles
from loguru import logger
from pydantic_settings import BaseSettings
import platformdirs


class Settings(BaseSettings):
    jira_base_url: str = 'http://127.0.0.1:8001'
    jira_project: str = ''
    jira_epic_jql: str = 'type = Epic'


settings: Settings | None = None


async def get_settings() -> Settings:
    global settings
    if not settings:
        settings = await load_settings()
    return settings

def get_data_dir() -> Path:
    return Path(platformdirs.user_data_dir('Jira deps', 'dkostromin'))

def get_settings_file_path() -> Path:
    return get_data_dir() / 'settings.json'

def ensure_data_dir_exists():
    data_dir = get_data_dir()
    try:
        mkdir(data_dir)
    except FileExistsError:
        pass

async def load_settings() -> Settings:
    try:
        async with aiofiles.open(get_settings_file_path(), 'r') as f:
            json_data = await f.read()
            data = json.loads(json_data)
            return Settings(**data)
    except Exception:
        logger.info('No settings file found, using default settings')
        return Settings()

async def save_settings(next_settings: Settings):
    global settings

    ensure_data_dir_exists()

    async with aiofiles.open(get_settings_file_path(), 'w') as f:
        json_data = json.dumps(dict(next_settings))
        await f.write(json_data)
        settings = next_settings
