# Telegram Tribute bot hook

Accepts messages from [@tribute](https://t.me/tribute) bot:
* Forwards it into other chat
* Send it with parsed info into webhook url (with optional auth)

Bot requires login into telegram account: `python -m app login`

> Supports only Russian messages, probably English will be there in the future, feel free to contribute

Simple settings (put into .env or set as env var):
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
# optional, attemts to send webhook request until 2xx status (default 3)
webhook_attempts=3
```
