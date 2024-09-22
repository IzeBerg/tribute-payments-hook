import dataclasses
import logging
import re
from enum import Enum

import aiohttp
from telethon import TelegramClient, events
from telethon.tl import types

from app.settings import settings
from app.utils import async_retry, jsonify, tg_client

logger = logging.getLogger(__name__)

CURRENCIES = {
    "₽": "RUB",
    "$": "USD",
    "€": "EUR",
}
AMOUNT_RE = re.compile(f"([{''.join(CURRENCIES.keys())}])([0-9,]+).([0-9]{{2}})")


class MessageType(Enum):
    payment = "payment"
    subscription = "subscription"


@dataclasses.dataclass
class ParsedMessage:
    user_id: int
    user_name: str
    amount: float
    currency: str
    comment: str | None
    message_type: MessageType
    message_id: int

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "amount": self.amount,
            "currency": self.currency,
            "comment": self.comment,
            "message_type": self.message_type,
            "message_id": self.message_id,
        }


async def run():
    async with tg_client() as tg:
        await run_with_client(tg)


async def run_with_client(tg: TelegramClient):
    peer = await tg.get_entity(settings.telegram_incoming_from)
    logger.info(f"Waiting messages from {peer}")
    tg.add_event_handler(
        on_incoming_message,
        events.NewMessage(
            incoming=True,
            from_users=peer,
        ),
    )
    await tg.run_until_disconnected()


async def on_incoming_message(event: events.NewMessage.Event):
    logger.debug(f"handle message {event}")
    if settings.telegram_forward_to:
        logger.debug(f"Forward message {event.message.id} from {event.message.peer_id}")
        await event.client.forward_messages(
            entity=settings.telegram_forward_to,
            messages=event.message,
            from_peer=event.message.peer_id,
        )

    if await handle_message(event.client, event.message):
        logger.info(f"Handled message {event.message.id} from {event.message.peer_id}")


async def handle_message(tg: TelegramClient, message: types.Message):
    parsed = await parse_message_russian(
        tg=tg,
        message_id=message.id,
        message=message.message,
        entities=message.entities,
    )
    logger.debug(f"message parsed {parsed}")

    if parsed:
        await post_message_data(message, parsed)
        return True
    return False


@async_retry(settings.webhook_attempts)
async def post_message_data(message: types.Message, parsed: ParsedMessage):
    if settings.webhook_url is None:
        return

    auth = None
    if settings.webhook_login and settings.webhook_password:
        auth = aiohttp.BasicAuth(settings.webhook_login, settings.webhook_password)

    logger.info(f"Try to post message {message.id} from {message.peer_id}: {parsed}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            settings.webhook_url,
            auth=auth,
            json=jsonify(
                {
                    "message": message.to_dict(),
                    "parsed": parsed.to_dict(),
                }
            ),
        ) as resp:
            resp.raise_for_status()


async def parse_message_russian(
    tg: TelegramClient,
    message_id: int,
    message: str,
    entities: list[types.TypeMessageEntity] | None,
) -> ParsedMessage | None:
    if not entities:
        return None
    if not message.startswith("Пользователь"):
        return None

    user_id = None
    user_name = None
    amount = None
    currency = None
    comment = None
    message_type = None

    for entity in entities:
        entity_part = message[entity.offset : entity.offset + entity.length]

        if user_id is None:
            if isinstance(entity, types.MessageEntityMentionName):
                user_id = int(entity.user_id)
                user_name = entity_part

            if isinstance(entity, types.MessageEntityMention):
                user_name = entity_part
                user = await tg.get_entity(user_name)
                user_id = user.id

            if user_id is not None:
                message_after_user = message[entity.offset + entity.length :].strip()
                if message_after_user.startswith("отправил"):
                    message_type = MessageType.payment
                elif message_after_user.startswith("оформил подписку"):
                    message_type = MessageType.subscription

        if comment is None:
            if isinstance(entity, types.MessageEntityBlockquote):
                comment = entity_part

        if amount is None:
            if isinstance(entity, types.MessageEntityBold):
                if amount_match := AMOUNT_RE.fullmatch(entity_part):
                    currency_chr, amount_str, decimals_str = amount_match.groups()
                    currency = CURRENCIES[currency_chr]
                    amount = int(amount_str.replace(",", "")) + int(decimals_str) / 100

    if (
        user_id is None
        or user_name is None
        or amount is None
        or currency is None
        or message_type is None
    ):
        # raise ValueError("incomplete data")
        logger.warning(f"Unfiltered message with incomplete data id={message_id}!")
        return None

    return ParsedMessage(
        user_id=user_id,
        user_name=user_name,
        amount=amount,
        currency=currency,
        comment=comment,
        message_type=message_type,
        message_id=message_id,
    )
