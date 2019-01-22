# My Little Face When Telegram Bot

This is the code which powers https://t.me/mlfwbot, but currently https://mylittlefacewhen.com is down or gone.

## Environment Variables
You need to define your `TG_API_KEY` environment variable, which is the telegram API key.
If you mount the container at `example.com````/mlfw`, you'll need to set `URL_PATH=mlfw` and `URL_HOSTNAME=example.com`.

You need to specify those when starting this container,
either via flag for the `docker` command,
or via `docker-compose.override.yml` file.
