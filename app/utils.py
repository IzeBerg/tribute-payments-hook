import datetime
import enum
import functools
import os.path
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, TypeVar

from telethon import TelegramClient
from telethon.sessions import StringSession

from app.settings import settings

T = TypeVar("T")


@asynccontextmanager
async def tg_client(new_session=False) -> AsyncIterator[TelegramClient]:
    if new_session:
        session = StringSession()
    else:
        session = load_session()

    async with TelegramClient(
        session=session,
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        sequential_updates=True,
    ) as client:
        save_session(session)

        try:
            yield client
        finally:
            save_session(session)


def get_session_path() -> str:
    return os.path.join(settings.telegram_session_path, "session.dat")


def load_session() -> StringSession:
    session_path = get_session_path()
    if os.path.exists(session_path):
        with open(session_path, "r") as fd:
            return StringSession(fd.read())
    return StringSession()


def save_session(session: StringSession):
    with open(os.path.join(settings.telegram_session_path, "session.dat"), "w") as fd:
        fd.write(session.save())


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
