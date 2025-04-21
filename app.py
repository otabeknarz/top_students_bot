import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.deep_linking import create_start_link

from modules.filters import TextEqualsFilter
from modules.functions import get_user, add_user, get_or_create_invitation, invite_user, get_users
from modules.keyboards import get_ok_keyboard, get_channels_keyboards


class GetStartTokenState(StatesGroup):
    link = State()


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
- Share your referral link and make sure 3 people register through the bot

If you have any questions, contact @e_rahimjon!""",
    "HERE_ARE_THE_CHANNELS_RESPONSE": "Here are the list of channels to follow:",
    "ALL_CHANNELS_SUBSCRIBED": lambda who, link: f"""🚀 {who} is inviting you to "TOP Students" marathon -  knowledge worth of nearly two million U.S. dollars 

Imagine a group of students accepted into some of the best universities in the world teaching you everything they know about admissions to universities abroad. No need to imagine. It is here.
Join us on a 5-day-admissions marathon where you will learn every bits of applying to TOP colleges in the U.S. and beyond. 

❕ Requirements to join:

- register through the bot
- invite 3 of your friends to the marathon 

🎁 We are also giving out 10 consultations for free during the marathon:

- 5 consultations to the participants who invited the most number of their friends 
- during the webinars, you can donate. Everyday the person to donate the most amount of money will receive a consultation. (All the money donated will  be given to a charity)

🗓 Dates: April 21-25

🔽Join:

{link}""",
    "CONGRATULATIONS_RESPONSE": lambda link: f"""Congratulations!
You have done completed all the tasks. Here is your link to join our Marathon: {link}.
Good Luck! See you in the marathon!"""
}

ERROR = "An unexpected error occurred on the server. Please try again later. /start"


async def check_subscribed(user_id: str | int, channel_id: str | int) -> bool:
    status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    return status.status != "left"


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    message_split = message.text.split(" ")
    token = None
    if len(message_split) == 2:
        token = message_split[1]

    if token:
        await state.update_data(token=token)

    state_data = await state.get_data()
    print(state_data)

    get_response = await get_user(message.from_user.id)
    if get_response.status != 200:
        add_response = await add_user(
            {
                "id": str(message.from_user.id),
                "username": message.from_user.username if message.from_user.username else str(message.from_user.id),
                "name": message.from_user.full_name,
            }
        )
        if add_response.status != 201:
            await message.answer(RESPONSES.get("SERVER_ERROR_RESPONSE", ERROR))
        else:
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


@dp.message(TextEqualsFilter("send links"))
async def ok_handler(message: Message) -> None:
    response = await get_users()
    if response.status != 200:
        await message.answer(RESPONSES.get("SERVER_ERROR_RESPONSE", ERROR) + "\n" + await response.text())
        return
    users = await response.json()[:3]
    sent_count = 0
    for user in users:
        link = "https://t.me/+OpLSPUn-La42NzEy"
        try:
            await bot.send_message(user.get("id"), RESPONSES.get("CONGRATULATIONS_RESPONSE")(link))
            print(f"sent {user.get('username')} {user.get('name')}")
            sent_count += 1
        except:
            pass
        await asyncio.sleep(0.5)
    await message.answer(f"{sent_count} users were sent successfully\noverall {len(users)}")


@dp.callback_query()
async def callback_query_handler(call: CallbackQuery, state: FSMContext) -> None:
    if call.data == "subscribed":
        status = []
        for channel in CHANNELS:
            status.append(await check_subscribed(call.message.chat.id, channel.get("id")))
        if all(status):
            response = await get_or_create_invitation(call.message.chat.id)
            if response.status in (200, 201):
                json_response = await response.json()
                state_data = await state.get_data()
                print(state_data)
                token = state_data.get("token")
                if token:
                    invite_response = await invite_user(call.from_user.id, token)
                    if invite_response.status == 200:
                        json_res = await invite_response.json()
                        await bot.send_message(json_res.get("user_id"),
                                               f"{call.message.from_user.full_name} has clicked start with your invitation link")
                        if json_res.get("count") == 3 and json_res.get("user_id"):
                            invite_link = "https://t.me/+OpLSPUn-La42NzEy"
                            await bot.send_message(json_res.get("user_id"), RESPONSES.get("CONGRATULATIONS_RESPONSE")(invite_link))
                link = await create_start_link(bot=bot, payload=json_response.get("token"))
                photo = FSInputFile(path="image.jpg")
                await call.message.answer_photo(photo=photo, caption=RESPONSES.get("ALL_CHANNELS_SUBSCRIBED", ERROR)(
                    f"@{call.from_user.username}"
                    if call.from_user.username
                    else call.from_user.full_name,
                    link
                ))
                await asyncio.sleep(0.5)
                await call.message.answer("Forward this message to at least 3 of your friends and make sure they register. Once 3 of them accomplish this, you will get the private link for our marathon channel.")
        else:
            await call.message.delete()
            await call.answer("Please join all our channels", show_alert=True)
            await call.message.answer(RESPONSES.get("HERE_ARE_THE_CHANNELS_RESPONSE", ERROR), reply_markup=get_channels_keyboards())


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
