from aiogram import Bot, types, Dispatcher, executor
import logging

import markups
from data import config
from db import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
db = Database('database.db')


async def check_sub_channels(channels, user_id):
    for channel in channels:
        chat_member = await bot.get_chat_member(chat_id=channel[1], user_id=user_id)
        if chat_member['status'] == 'left':
            return False
    return True


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if await check_sub_channels(config.CHANNELS, message.from_user.id):
            if not db.user_exists(message.from_user.id):
                start_command = message.text
                referrer_id = str(start_command[7:])
                if str(referrer_id) != "":
                    if str(referrer_id) != str(message.from_user.id):
                        db.add_user(message.from_user.id, referrer_id)
                        try:
                            await bot.send_message(referrer_id, "У Вас новый реферал!")
                        except:
                            pass
                    else:
                        await bot.send_message(message.from_user.id, "Ну ты и хитрый! Нельзя быть своим рефералом!")
                else:
                    db.add_user(message.from_user.id)
            else:
                await bot.send_message(message.from_user.id, "Вы уже участвуете в аэрдропе!",
                                       reply_markup=markups.profile_keyboard)

            await bot.send_message(message.from_user.id, "Нажмите реф программа", reply_markup=markups.profile_keyboard)
        else:
            await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                                   reply_markup=markups.show_channels())


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if await check_sub_channels(config.CHANNELS, message.from_user.id):
            if message.text == 'Реферальная программа':
                await bot.send_message(message.from_user.id,
                                       f"Your ID: {message.from_user.id}\n"
                                       f"https://t.me/{config.BOT_NICKNAME}?start={message.from_user.id}\n"
                                       f"Количество рефералов: {db.count_referrals(message.from_user.id)}")
            elif message.text == 'О конкурсе':
                await bot.send_message(message.from_user.id, "Правила конкурса")
        else:
            await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                                   reply_markup=markups.show_channels())


@dp.callback_query_handler(text="sub_channel_done")
async def sub_channel_done(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)

    if await check_sub_channels(config.CHANNELS, message.from_user.id):
        await bot.send_message(message.from_user.id, "Hello", reply_markup=markups.profile_keyboard)
    else:
        await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                               reply_markup=markups.show_channels())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
