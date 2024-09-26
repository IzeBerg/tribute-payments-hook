import datetime
import enum
import functools
import json
import os.path
from typing import Any, Self, TypeVar

from atomicwrites import atomic_write
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.settings import settings

T = TypeVar("T")


class DataStorage:
    STORAGE_PATH = os.path.join(settings.telegram_session_path, "data.dat")

    def __init__(self):
        super().__init__()

        self.data = {}
        self.read()

    def read(self):
        if os.path.exists(self.STORAGE_PATH):
            with open(self.STORAGE_PATH, "r") as fd:
                self.data = json.load(fd)

    def get(self, key: str, default: Any) -> Any:
        return self.data.get(key, default)

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def save(self):
        with atomic_write(self.STORAGE_PATH, overwrite=True) as fd:
            json.dump(self.data, fd)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class TelegramSession(StringSession):
    SESSION_PATH = os.path.join(settings.telegram_session_path, "session.dat")

    def __init__(self, new_session: bool = False):
        super().__init__(None if new_session else self.read())

    def read(self):
        if os.path.exists(self.SESSION_PATH):
            with open(self.SESSION_PATH, "r") as fd:
                return fd.read()

    def save(self):
        with atomic_write(self.SESSION_PATH, overwrite=True) as fd:
            fd.write(super().save())


def tg_client(new_session=False) -> TelegramClient:
    return TelegramClient(
        session=TelegramSession(new_session=new_session),
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
    )


def jsonify(data: Any) -> Any:
    if isinstance(data, (set, list, tuple)):
        return [jsonify(x) for x in data]
    if isinstance(data, dict):
        return {jsonify(k): jsonify(v) for k, v in data.items()}
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    if isinstance(data, enum.Enum):
        return data.value
    return data


def async_retry(max_attempts: int):
    if max_attempts < 1:
        raise ValueError("attempts must be 1 or more")

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except:  # noqa
                    if attempt == max_attempts - 1:
                        raise

        return wrapped

    return wrapper
