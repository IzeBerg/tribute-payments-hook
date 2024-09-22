import logging

from app.utils import tg_client

logger = logging.getLogger(__name__)


async def run():
    async with tg_client(new_session=True):
        logger.info("Login complete!")
