> This version is outdated, better use https://github.com/izeberg/go-tribute-payments-hook

# Telegram Tribute bot hook

Accepts messages from [@tribute](https://t.me/tribute) bot:
* Forwards it into other chat
* Send it with parsed info into webhook url (with optional auth)
* Initially fetches all messages from history

Bot requires login into telegram account: `python -m app login`

> The microservice guarantees that each message will be delivered or forwarded at least once. However, it cannot guarantee that the message will only be delivered once. Handling duplicate messages is the responsibility of the webhook receiver (for example, use message_id as a unique constraint).

> Supports only Russian messages, probably English will be there in the future, feel free to contribute

## Docker
Everything could be run in docker, just use image [izeberg/tribute-payments-hook](https://hub.docker.com/repository/docker/izeberg/tribute-payments-hook).

## Settings
Application could be configured with environment variables defined here [./app/settings.py](./app/settings.py).

Here's example:
```
# get credentials from https://my.telegram.org
telegram_api_id=<api_id>
telegram_api_hash=<api_hash>

# peer id where messages will be accepted to processing
telegram_incoming_from=@trubute

# optional, this is where session will be stored (default /session)
telegram_session_path=/session

# optional, peer id to forward message, for channels/groups add -100 before
telegram_forward_to=-1001111111111

# optional url where HTTP POST with info will be sent
webhook_url=https://example.com/tribute
# optional basic auth parameters
webhook_login=user
webhook_password=pwd
# optional hmac signature key for webhook's body
webhook_signature_key=supersecretKey

# optional, but strictly recommended, default None
# date/datetime in ISO format
# messages *after* to this date will be retrieved for inital start
# otherwise messages will be retrived from the begginning of history
initial_messages_offset_dt=2024-09-26

# optional, default False
# handling output (sent by you) messages
handle_out_messages=False

# optional, default True
# forward only valid/parsed messages to `telegram_forward_to` chat
forward_only_parsed=True
```
