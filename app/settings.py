import datetime
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    debug: bool = False

    telegram_api_id: int
    telegram_api_hash: str

    telegram_session_path: str = Field(
        "/session",
        description="Persistent path where session session files will be saved",
    )

    telegram_incoming_from: int | str = Field(
        description="peer id where messages will be accepted to processing",
        union_mode="left_to_right",
    )

    telegram_forward_to: int | str | None = Field(
        None,
        description="peer id to forward message, for channels/groups add -100 before",
        union_mode="left_to_right",
    )

    forward_only_parsed: bool = Field(
        default=True,
        description="Forward only parsed messages",
    )

    handle_out_messages: bool = Field(
        default=False,
        description="Handle messages that sent by you",
    )

    webhook_url: str | None = Field(
        None,
        description="HTTP URL to send processed messages",
    )
    webhook_login: str | None = None
    webhook_password: str | None = None
    webhook_attempts: int = Field(
        default=3,
        description="Retries to send webhook message until application failure",
    )

    fetch_messages_attempts: int = Field(
        default=3,
        description="Retries to fetch recent messages from bot until application failure",
    )

    initial_messages_offset_dt: datetime.datetime | None = Field(
        default=None,
        description="Offset date (messages *after* to this date will be retrieved).",
    )


settings = Settings()


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s:%(process)d:%(levelname)s:%(name)s:%(message)s",
)
