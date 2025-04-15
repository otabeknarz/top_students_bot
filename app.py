import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from modules.filters import TextEqualsFilter
from modules.functions import get_user, add_user, update_user, get_or_create_invitation, invite_user
from modules.keyboards import get_ok_keyboard, get_channels_keyboards

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

CHANNELS = [
    {"id": -1002064715991, "name": "Parvoz", "link": "https://t.me/parvozlc"},
    {"id": -1001825051597, "name": "Azizbek Zaylobiddinov", "link": "https://t.me/abdulazizziy"},
    {"id": -1001661528628, "name": "Asilbek Ashurov", "link": "https://t.me/notasill"},
    {"id": -1002540462125, "name": "Jasurbek Umarov", "link": "https://t.me/Jasurbek_Umarovs"},
    {"id": -1002245418335, "name": "Jamshidbek Izzatulloh", "link": "https://t.me/Jamshidbek_Izzatulloh"},
    {"id": -1002401664810, "name": "Ruhshona Sobirova", "link": "https://t.me/ruhshonatpenn"}
]

RESPONSES = {
    # Errors
    "SERVER_ERROR_RESPONSES": "An unexpected error occurred on the server. Please try again later.",
    # Successes
    "WELCOME_RESPONSE": """Assalamu alaykum. We are happy that you are willing to join our marathon! 

To get the link of a private channel, you MUST do the following actions:
- Follow all the required channels of marathon organizers
- Share your referral link and make sure 3 people will use the bot

If you have any questions, contact @e_rahimjon!""",
    "HERE_ARE_THE_CHANNELS_RESPONSE": "Here are the list of channels to follow:",
    "ALL_CHANNELS_SUBSCRIBED": lambda link: f"Here is your referral link —> {link}. Once 3 people go to bot from your link and join all the channels, we will give you a private link to join marathon channel. By the way, the one whose referral link is used the most will be gifted with FREE Consultation!",
}

ERROR = "An unexpected error occurred on the server. Please try again later. /start"


async def check_subscribed(user_id: str | int, channel_id: str | int) -> bool:
    status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return status.status != "left"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    message_split = message.text.split(" ")
    token = None
    if len(message_split) == 2:
        token = message_split[1]

    get_response = await get_user(message.from_user.id)
    if get_response.status != 200:
        add_response = await add_user(
            {
                "id": str(message.from_user.id),
                "username": message.from_user.username,
                "name": message.from_user.full_name,
            }
        )
        if add_response.status != 201:
            await message.answer(RESPONSES.get("SERVER_ERROR_RESPONSE", ERROR))
        else:
            if token:
                invite_response = await invite_user(message.from_user.id, token)
                if invite_response.status == 200:
                    json_response = await invite_response.json()
                    await bot.send_message(json_response.get("user_id"),
                                           f"You have successfully invited {message.from_user.full_name}\nYour invitations count: {json_response.get('count')}")
            await message.answer(
                RESPONSES.get("WELCOME_RESPONSE", ERROR), reply_markup=get_ok_keyboard()
            )
    else:
        await message.answer(
            RESPONSES.get("WELCOME_RESPONSE", ERROR), reply_markup=get_ok_keyboard()
        )


@dp.message(TextEqualsFilter("OK ✅"))
async def ok_handler(message: Message) -> None:
    await message.answer(RESPONSES.get("HERE_ARE_THE_CHANNELS_RESPONSE", ERROR), reply_markup=get_channels_keyboards())


@dp.callback_query()
async def callback_query_handler(call: CallbackQuery) -> None:
    if call.data == "subscribed":
        status = []
        for channel in CHANNELS:
            status.append(await check_subscribed(call.message.chat.id, channel.get("id")))
        if all(status):
            response = await get_or_create_invitation(call.message.chat.id)
            if response.status in (200, 201):
                json_response = await response.json()
                link = await create_start_link(bot=bot, payload=json_response.get("token"))
                await call.message.answer(RESPONSES.get("ALL_CHANNELS_SUBSCRIBED", ERROR)(link))
        else:
            await call.message.delete()
            await call.answer("Please join all our channels", show_alert=True)
            await call.message.answer(RESPONSES.get("HERE_ARE_THE_CHANNELS_RESPONSE", ERROR), reply_markup=get_channels_keyboards())


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
