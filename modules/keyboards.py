from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

CHANNELS = [
    {"name": "Parvoz", "link": "https://t.me/parvozlc",},
    {"name": "Azizbek Zaylobiddinov", "link": "https://t.me/abdulazizziy"},
    {"name": "Asilbek Ashurov", "link": "https://t.me/notasill"},
    {"name": "Jasurbek Umarov", "link": "https://t.me/Jasurbek_Umarovs"},
    {"name": "Jamshidbek Izzatulloh", "link": "https://t.me/Jamshidbek_Izzatulloh"},
    {"name": "Ruhshona Sobirova", "link": "https://t.me/ruhshonatpenn"}
]


def get_channels_keyboards():
    inline_buttons = [
        [InlineKeyboardButton(text=channel.get("name"), url=channel.get("link"))] for channel in CHANNELS
    ]
    inline_buttons.append([InlineKeyboardButton(text="I've joined them all ✅", callback_data="subscribed")])
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


def get_ok_keyboard(): return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="OK ✅")]], resize_keyboard=False)
