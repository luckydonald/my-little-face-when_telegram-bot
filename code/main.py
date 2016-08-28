# -*- coding: utf-8 -*-
import requests
from DictObject import DictObject
from flask import Flask
from flask import request
from luckydonaldUtils.logger import logging
from pytgbot import Bot
from pytgbot.api_types.receivable.updates import Update

from secrets import API_KEY, HOSTNAME
from api import MLFW

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)

VERSION = "1.3.1"
__version__ = VERSION

app = Flask(__name__)
bot = Bot(API_KEY, return_python_objects=False)
# Set `return_python_objects=False`
# because we need to be really fast to answer inline queries in time,
# and my computer is crap,
# so any nanosecond this adds is too much,
# resulting in the queries timing out.

username = bot.get_me().username
logging.add_colored_handler(level=logging.DEBUG)

mlfw = MLFW(bot)


@app.route("/info/<command>")
def info(command):
    """
    Issue commands. E.g. /info/getMe

    :param command:
    :return:
    """
    logger.debug("COMMAND: {cmd}, ARGS: {args}".format(cmd=command, args=request.args))
    import json
    return json.dumps(bot.do(command, **request.args))


@app.route("/host")
def host():
    """
    Get infos about your host, like IP etc.
    :return:
    """
    import json
    import socket
    info = requests.get('http://ipinfo.io').json()
    info["host"] = socket.gethostname()
    info["version"] = VERSION
    return json.dumps(info)
# end def


@app.route("/init")
def init():
    path = "/bot/" + API_KEY + "/income"
    hostname = HOSTNAME
    if not hostname:
        info = DictObject.objectify(requests.get('http://ipinfo.io').json())
        logger.info("PATH: {}".format(info))
        hostname = str(info.ip)
    # end if
    webhook_url = "https://" + hostname + "/dumper" + path
    logger.success("URL: {}".format(webhook_url))
    logger.debug(bot.set_webhook())

    # In case sending a custom public key
    # from pytgbot.api_types.sendable import InputFile
    # response = bot.set_webhook(webhook_url, certificate=InputFile("/certs/ YOUR FILE"))

    # In case of a valid HTTPS host, you can go with:
    response = bot.set_webhook(webhook_url)

    logger.success(response)
    import json
    return json.dumps({"status": "ok", "webhook": webhook_url, "response": response})
# end def


@app.route("/bot/<api_key>/income", methods=['POST'])
def income(api_key):
    if api_key != API_KEY:
        error_msg = "Wrong API key: {wrong_key}".format(wrong_key=api_key)
        logger.warning(error_msg)
        return error_msg, 403
    from pprint import pformat
    logger.info("INCOME:\n{}\n\nHEADER:\n{}".format(
        pformat(request.get_json()),
        request.headers if hasattr(request, "headers") else None
    ))
    update = Update.from_array(request.get_json())
    logger.debug("UPDATE: {}".format(update))
    # assert isinstance(msg, Message)
    if "inline_query" in update and not update.inline_query:
        logger.debug("Skipping update without inline query.")
        return "ok"
    inline_query_id = update.inline_query.id
    query = update.inline_query.query
    query_offset = update.inline_query.offset
    mlfw.search(query, inline_query_id, offset=query_offset)
# end def


@app.route("/")
def hello():
    return "Your advertisements could be here!"


if __name__ == "__main__":  # no nginx
    # "__main__" means, this python file is called directly.
    # not to be confused with "main" (because main.py) when called from from nginx
    app.run(host='0.0.0.0', debug=True, port=80)  # python development server if no nginx
# end if

