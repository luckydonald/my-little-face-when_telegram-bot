# My Little Face When Telegram Bot

This is the code which powers https://t.me/mlfwbot, but currently https://mylittlefacewhen.com is down or gone.

## Running
```bash
docker-compose up -d
```
In my setup a reverse proxy is mounting it at `example.com/mlfw`,
which exposes the container's port `80` to the world.

## Sample reverse proxy config
This is a very simple sample nginx config to get you started.
```nginx
server {
    listen 80;

    location /mlfw {
        proxy_pass http://mlfw/$url?$query_string;
        proxy_set_header X-Host $host;
        proxy_set_header X-Incoming-IP $remote_addr;
    }
}
```


## Environment Variables
You need to define your `TG_API_KEY` environment variable, which is the telegram API key.
If you mount the container at `example.com/mlfw`, you'll need to set `URL_PATH=mlfw` and `URL_HOSTNAME=example.com`.

You need to specify those when starting this container,
either via flag for the `docker` command,
or via `docker-compose.yml` file (or a separate `docker-compose.override.yml` if you want to keep everything clean).
