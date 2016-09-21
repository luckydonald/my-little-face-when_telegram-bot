# -*- coding: utf-8 -*-
from json import dumps

import requests
from DictObject import DictObject
from luckydonaldUtils.logger import logging
from pytgbot.api_types.sendable.inline import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultGif, \
    InlineQueryResultPhoto
from pytgbot.exceptions import TgApiException, TgApiServerException, TgApiParseException


__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


class MLFW(object):
    START_TEXT = "This bot can help you find and share images from mylittlefacewhen.com.\n" \
                 "It works automatically, no need to add it anywhere. " \
                 "Simply open any of your chats and type <code>@{username} something</code> in the message field. " \
                 "Then tap on a result to send.\n" \
                 "\n" \
                 "For example, try typing <code>@{username} i need pictures</code> here."

    HELP_TEXT = START_TEXT

    root = "http://mylittlefacewhen.com/"
    tag_search = "http://mylittlefacewhen.com/api/v2/tag/"
    tag_info = "http://mylittlefacewhen.com/api/v2/face/"
    error_image = "http://www.iconsdb.com/icons/preview/red/warning-xxl.png"

    def __init__(self, bot):
        super(MLFW, self).__init__()
        self.bot = bot
    # end def

    def search(self, string, inline_query_id, offset):
        if not string or string.lower().strip() == "best pony":  # nothing entered.
            string = "littlepip"
        results = []
        next_offset=None
        if offset is None or len(str(offset).strip()) < 1:
            offset = 0
        else:
            offset = int(offset)
        valid_tag_names = []
        for string_part in string.split(","):
            string_part = string_part.strip()
            valid_tag_obj = get_json(self.tag_search, params=dict(format="json", name__startswith=string_part, limit=1))
            if "error" in valid_tag_obj:
                error_message = InlineQueryResultArticle(
                    id="404e:"+string,
                    title=u"\"{tag}\" not found.".format(tag=string),
                    input_message_content=InputTextMessageContent(string),
                    description=valid_tag_obj.error, thumb_url=self.error_image
                )
                try:
                    logger.debug("Sending result: {}".format((inline_query_id, [error_message])))
                    result = self.check_result(self.bot.answer_inline_query(inline_query_id, [error_message]))
                    logger.success(result)
                except TgApiException:
                    logger.exception("Answering query failed.")
                return
            for tag_obj in valid_tag_obj.objects:
                valid_tag_names.append(tag_obj.name)
        if len(valid_tag_names) == 0:
            result = InlineQueryResultArticle(
                    id="404t:"+string,
                    title=u"\"{tag}\" not found.".format(tag=string),
                    input_message_content=InputTextMessageContent(string),
                    description="No similar tag found.",
                    thumb_url=self.error_image
            )
            try:
                logger.debug("Sending result: {}".format((inline_query_id, result)))
                result = self.check_result(self.bot.answer_inline_query(inline_query_id, result))
                logger.success(result)
            except TgApiException as e:
                logger.exception("Answering query failed: {e}".format(e=e))
            return
        logger.info("tags: {}".format(valid_tag_names))
        logger.debug("offset: {}".format(offset))
        images_of_tag = get_json(self.tag_info, params=dict(search=dumps(valid_tag_names), format="json", limit=10, offset=offset))
        logger.debug(images_of_tag)
        if images_of_tag.meta.total_count < 1 or len(images_of_tag.objects) < 1:
            error_message = InlineQueryResultArticle(
                id="404i:"+string,
                title=u"\"{tag}\" not found.".format(tag=string),
                input_message_content=InputTextMessageContent(string),
                description="Search results no images.",
                thumb_url=self.error_image
            )
            try:
                logger.debug("Sending result: {}".format((inline_query_id, [error_message])))
                result = self.check_result(self.bot.answer_inline_query(inline_query_id, [error_message]))
                logger.success(result)
            except TgApiException as e:
                logger.exception("Answering query failed: {e}".format(e=e))
            return
        if images_of_tag.meta.next:
            next_offset = offset+10
        for img in images_of_tag.objects:
            # image = self.root + tag.objects[0].resizes.small
            image_full = self.root + img.image
            image_small = image_full
            if "resizes" in img and "small" in img.resizes:
                image_small = self.root + img.resizes.small
            if "thumbnails" in img:
                if "png" in img.thumbnails:
                    image_small = self.root + img.thumbnails.png
                elif "jpg" in img.thumbnails:
                    image_small = self.root + img.thumbnails.jpg
            image_gif = self.root + img.thumbnails.gif if "gif" in img.thumbnails else None
            tag_total_count = images_of_tag.meta.total_count
            id = "mlfw-{id}".format(id=img.id)
            if not id:
                logger.error("NO ID: {}".format(img))
                continue
            logger.debug("id: {id}".format(id=id))
            # results.append(InlineQueryResultArticle(id=id, thumb_url=image_small, title=u"{tag}".format(tag=img.title), message_text=image_full, description=img.description))
            if image_gif:
                results.append(InlineQueryResultGif(
                    id=id, title=img.title, gif_url=image_full, thumb_url=image_small,
                    caption=self.str_to_caption(string), gif_height=img.height, gif_width=img.width
                ))
            else:
                results.append(InlineQueryResultPhoto(
                    id=id, title=img.title, photo_url=image_full, thumb_url=image_small,
                    caption=self.str_to_caption(string), photo_height=img.height, photo_width=img.width
                ))
        for res in results:
            logger.debug(res.to_array())
        logger.debug("next_offset=" + str(next_offset))
        try:
            logger.debug("Sending result: {}, cache_time=300, next_offset={next_offset}".format((inline_query_id, results), next_offset=next_offset))
            result = self.check_result(self.bot.answer_inline_query(inline_query_id, results, cache_time=300, next_offset=next_offset))
            logger.success(result)
        except TgApiException as e:
            logger.exception("Answering query failed: {e}".format(e=e))
            # end try
    # end def

    @staticmethod
    def str_to_caption(search_string):
        search_string = search_string.strip()
        if search_string.lower() == "littlepip":
            return "#littlepip #best_pony"
        # end def
        return "#{search}".format(search=search_string.strip().lower().replace(" ", "_"))
    # end def str_to_caption


    def check_result(self, res):
        if res.ok != True:
            raise TgApiServerException(
                error_code=res.error_code if "error_code" in res else None,
                response=res.response if "response" in res else None,
                description=res.description if "description" in res else None,
            )
        # end if not ok
        if "result" not in res:
            raise TgApiParseException('Key "result" is missing.')
        # end if no result
        return res.result
    # end def
# end class

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X10.69; rv:4458.42) Gecko/4458 Firefox/69.0 Pon3Downloader'}


def get_json(url, objectify=True, **kwargs):
    kwargs.setdefault("headers", HEADERS)
    json = requests.get(url, **kwargs).json()
    if objectify:
        return DictObject.objectify(json)
    return json
# end def