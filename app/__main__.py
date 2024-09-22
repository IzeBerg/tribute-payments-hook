import argparse
import asyncio
from enum import Enum

from app.actions import login, worker


class ActionEnum(Enum):
    worker = "worker"
    login = "login"

    def __str__(self):
        return self.value


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        type=ActionEnum,
        choices=list(ActionEnum),
    )
    args = parser.parse_args()

    if args.action == ActionEnum.worker:
        await worker.run()
    elif args.action == ActionEnum.login:
        await login.run()
    else:
        raise Exception("unknown action")


if __name__ == "__main__":
    asyncio.run(main())
