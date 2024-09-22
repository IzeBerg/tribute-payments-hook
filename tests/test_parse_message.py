from unittest import mock

import pytest
from telethon.tl import types

from app.actions.worker import parse_message_russian


@pytest.mark.parametrize(
    "message,entities,user_name,amount,currency,comment",
    [
        (
            "Пользователь @aaaaaaa отправил ₽2000.11 на Любая сумма в рублях.\n\nСообщение:\naaaaaaa",
            [
                types.MessageEntityMention(
                    offset=13,
                    length=8,
                ),
                types.MessageEntityBold(
                    offset=31,
                    length=8,
                ),
                types.MessageEntityBold(
                    offset=43,
                    length=20,
                ),
                types.MessageEntityBlockquote(
                    offset=77,
                    length=7,
                ),
            ],
            "@aaaaaaa",
            2000.11,
            "RUB",
            "aaaaaaa",
        ),
        (
            "Пользователь @aaaaaaa отправил ₽2000.11 на Любая сумма в рублях.",
            [
                types.MessageEntityMention(
                    offset=13,
                    length=8,
                ),
                types.MessageEntityBold(
                    offset=31,
                    length=8,
                ),
                types.MessageEntityBold(
                    offset=43,
                    length=20,
                ),
            ],
            "@aaaaaaa",
            2000.11,
            "RUB",
            None,
        ),
        (
            "Пользователь @aaaaaaaaa оформил подписку на канал Ttttt TTT (@tttttttt) за ₽1000.01.",
            [
                types.MessageEntityMention(
                    offset=13,
                    length=10,
                ),
                types.MessageEntityBold(
                    offset=50,
                    length=9,
                ),
                types.MessageEntityMention(
                    offset=61,
                    length=9,
                ),
                types.MessageEntityBold(
                    offset=75,
                    length=8,
                ),
            ],
            "@aaaaaaaaa",
            1000.01,
            "RUB",
            None,
        ),
        (
            "Пользователь @aaaaaaaaaaaaaaaaaaa оформил подписку на канал Ttttt TTT (@tttttttt) за $100.00.",
            [
                types.MessageEntityMention(
                    offset=13,
                    length=20,
                ),
                types.MessageEntityBold(
                    offset=60,
                    length=9,
                ),
                types.MessageEntityMention(
                    offset=71,
                    length=9,
                ),
                types.MessageEntityBold(
                    offset=85,
                    length=7,
                ),
            ],
            "@aaaaaaaaaaaaaaaaaaa",
            100.00,
            "USD",
            None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_parse_message_russian(
    message,
    entities,
    user_name,
    amount,
    currency,
    comment,
):
    user = mock.MagicMock()
    user.id = 123

    async def get_entity_mock(*_):
        return user

    tg = mock.MagicMock()
    tg.get_entity = get_entity_mock

    parsed = await parse_message_russian(
        tg=tg,
        message_id=1111,
        message=message,
        entities=entities,
    )
    assert parsed.user_id == user.id
    assert parsed.user_name == user_name
    assert parsed.amount == amount
    assert parsed.currency == currency
    assert parsed.comment == comment
    assert parsed.message_id == 1111
