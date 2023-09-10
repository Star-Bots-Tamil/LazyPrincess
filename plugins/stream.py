from pyrogram import Client, filters, enums
from pyshorteners import Shortener
from info import *
from database.lazy_utils import progress_for_pyrogram, convert, humanbytes
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors import FloodWait, UserNotParticipant
import os 
import humanize
from util.human_readable import humanbytes
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash, get_media_file_size
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

async def get_channel_shortlink(link):
    url = 'https://{URL_SHORTENR_WEBSITE}/api'
    params = {'api': URL_SHORTNER_WEBSITE_API, 'url': link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
            data = await response.json()
            return data["shortenedUrl"]

def get_media_file_name(m):
    media = m.video or m.document
    if media and media.file_name:
        return urllib.parse.quote_plus(media.file_name)
    else:
        return None

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
        log_msg = await m.forward(chat_id=FILES_CHANNEL)
        file_name = get_media_file_name(m)
        file_hash = get_hash(log_msg, HASH_LENGTH)
        stream_link = "https://{}/{}/{}?hash={}".format(FQDN, log_msg.id, file_name, file_hash) if ON_HEROKU or NO_PORT else \
            "http://{}:{}/{}/{}?hash={}".format(FQDN,
                                    PORT,
                                    log_msg.id,
                                    file_name,
                                    file_hash)
        watch_link = "https://{}/Watch/{}/{}?hash={}".format(FQDN, log_msg.id, file_name, file_hash) if ON_HEROKU or NO_PORT else \
            "http://{}:{}/Watch/{}/{}?hash={}".format(FQDN,
                                    PORT,
                                    log_msg.id,
                                    file_name,
                                    file_hash)
        file_hash = get_hash(log_msg, HASH_LENGTH)
        file_name = get_name(log_msg)
        file_size = humanbytes(get_media_file_size(m))
        file_caption = m.caption
        shortened_stream_link = await get_shortlink(stream_link)
        shortened_watch_link = await get_shortlink(watch_link)

        msg_text ="""
<b>Your Link is Generated... ⚡\n
📁 File Name :- {}\n
📦 File Size :- {}\n
🔠 File Captain :- {}\n
📥 Fast Download Link :- {}\n
🖥 Watch Link :- {}\n
❗ Note :- This Link is Permanent and Won't Gets Expired 🚫\n
©️ <a href=https://t.me/Star_Bots_Tamil><b></b>Star Bots Tamil</a></b></b>"""

        await log_msg.reply_text(text=f"<b>Request By :- <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>\nID :- <code>{m.from_user.id}</code>\n📥 Download Link :- {stream_link}</b>", disable_web_page_preview=True, parse_mode=ParseMode.HTML, quote=True)
        await m.reply_text(
            text=msg_text.format(file_name, file_size, file_caption, shortened_stream_link, shortened_watch_link),
            parse_mode=ParseMode.HTML, 
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Fast Download Link", url=shortened_stream_link)], [InlineKeyboardButton("🖥 Watch Link", url=shortened_watch_link)], [InlineKeyboardButton("🎥 Movie Updates", url="https://t.me/Star_Moviess_Tamil")], [InlineKeyboardButton("🔥 Update Channel", url="https://t.me/Star_Bots_Tamil")]]),
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=FILES_CHANNEL, text=f"<b>Got FloodWait of {str(e.x)}s from <a href=tg://user?id={m.from_user.id}>{m.from_user.first_name}</a>\n\nUser ID :- <code>{str(m.from_user.id)}</code></b>", disable_web_page_preview=True, parse_mode=ParseMode.HTML)


@Client.on_message(
    filters.channel
    & (
        filters.document
        | filters.video
    ),
    group=4,
)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=FILES_CHANNEL)
        file_name = get_media_file_name(broadcast)
        file_hash = get_hash(log_msg, HASH_LENGTH)
        stream_link = "https://{}Watch/{}/{}?hash={}".format(FQDN, log_msg.id, file_name, file_hash) if ON_HEROKU or NO_PORT else \
            "http://{}:{}Watch/{}/{}?hash={}".format(FQDN,
                                    PORT,
                                    log_msg.id,
                                    file_name,
                                    file_hash)
        shortened_link = await get_channel_shortlink(stream_link)

        await log_msg.reply_text(
            text=f"<b>Channel Name :- {broadcast.chat.title}\nChannel ID :- <code>{broadcast.chat.id}</code>\nRequest URL :- {stream_link}\nShortener Link :- {shortened_link}</b>",
            quote=True,
            parse_mode=ParseMode.HTML
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📥 Fast Download Link", url=shortened_link)]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=FILES_CHANNEL,
                             text=f"<b>Got FloodWait of {str(w.x)}s From {broadcast.chat.title}\n\nChannel ID :-</b> <code>{str(broadcast.chat.id)}</code>",
                             disable_web_page_preview=True, parse_mode=ParseMode.HTML)
    except Exception as e:
        await bot.send_message(chat_id=FILES_CHANNEL, text=f"<b>#Error_Trackback :-</b> <code>{e}</code>", disable_web_page_preview=True, parse_mode=ParseMode.HTML)
        print(f"Can't Edit Broadcast Message!\nError :- {e}")
