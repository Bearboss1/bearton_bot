from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from data.config import CHANNELS

btn_ref = KeyboardButton("Реферальная программа")
btn_help = KeyboardButton("О конкурсе")
profile_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_ref, btn_help)


def show_channels():
    keyboard = InlineKeyboardMarkup(row_width=2)

    for channel in CHANNELS:
        btn = InlineKeyboardButton(text=channel[0], url=channel[2])
        keyboard.insert(btn)

    btn_done_sub = InlineKeyboardButton(text="I am subscribed", callback_data="sub_channel_done")
    keyboard.insert(btn_done_sub)

    return keyboard
