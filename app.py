from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import InputFile

from captcha import Captcha
import logging
import random

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from middleware.throttling import rate_limit
import markups
from data import config
from db import Database
import middleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('database.db')
middleware.setup(dp)


def check_raffle_winner():
    users_list = db.get_users()
    new_users_list = []
    for user in users_list:
        for i in range(db.count_referrals(user) + 1):
            new_users_list.append(user)

    winner_id = random.choice(new_users_list)
    return winner_id


def check_best_refferer():
    users_list = db.get_users()
    count_refferals_list = []
    for user_id in users_list:
        count_refferals_list.append(db.count_referrals(user_id))
    not_sorted_list = zip(count_refferals_list, users_list)
    sorted_list = sorted(not_sorted_list, key=lambda tup: [0])

    winner_tuple = sorted_list[0]
    winner_id = winner_tuple[1]

    return winner_id


async def check_sub_channels(channels, user_id):
    for channel in channels:
        chat_member = await bot.get_chat_member(chat_id=channel[1], user_id=user_id)
        if chat_member['status'] == 'left':
            return False
    return True


@rate_limit(limit=2)
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        global start_command
        start_command = message.text
        if await check_sub_channels(config.CHANNELS, message.from_user.id):
            if not db.user_exists(message.from_user.id):
                splited = start_command.split()
                if len(splited) == 2:
                    referrer_id = splited[1]
                    if str(referrer_id) != str(message.from_user.id):
                        db.add_user(message.from_user.id, referrer_id)
                        try:
                            await bot.send_message(referrer_id, config.NEW_REF_MESSAGE)
                        except:
                            pass
                    else:
                        await bot.send_message(message.from_user.id, config.SELF_REF_MESSAGE)
                else:
                    db.add_user(message.from_user.id)
            else:
                await bot.send_message(message.from_user.id, config.TAKED_PART_MESSAGE,
                                       reply_markup=markups.profile_keyboard)

            await bot.send_message(message.from_user.id, config.WELCOME_MESSAGE, reply_markup=markups.profile_keyboard)
        else:
            await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                                   reply_markup=markups.show_channels())


@dp.message_handler(commands='check_winner')
async def end_raf(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == config.admin_id:
            await bot.send_message(message.from_user.id, config.WINNER_MESSAGE.format(check_raffle_winner(),
                                                                                      check_best_refferer()))


@dp.message_handler(commands='check_sub')
async def end_raf(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == config.admin_id:
            user_list = db.get_users()
            for user in user_list:
                if await check_sub_channels(config.CHANNELS, user):
                    pass
                else:
                    db.delete_user(user)


@rate_limit(limit=2)
@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if await check_sub_channels(config.CHANNELS, message.from_user.id):
            if message.text == 'Реферальная программа':
                await bot.send_message(message.from_user.id, config.REF_PROG_MESSAGE.format(
                    config.BOT_NICKNAME,
                    message.from_user.id,
                    db.count_referrals(message.from_user.id)))

            elif message.text == 'О конкурсе':
                photo = InputFile('media/100.png')
                await bot.send_photo(message.from_user.id, photo=photo, caption=config.ABOUT_MESSAGE)
        else:
            await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                                   reply_markup=markups.show_channels())


@rate_limit(limit=2)
@dp.callback_query_handler(text="sub_channel_done")
async def sub_channel_done(message: types.Message):

    await bot.delete_message(message.from_user.id, message.message.message_id)

    if await check_sub_channels(config.CHANNELS, message.from_user.id):
        if not db.user_exists(message.from_user.id):
            splited = start_command.split()
            if len(splited) == 2:
                referrer_id = splited[1]
                if str(referrer_id) != str(message.from_user.id):
                    db.add_user(message.from_user.id, referrer_id)
                    await bot.send_message(message.from_user.id, config.WELCOME_MESSAGE,
                                           reply_markup=markups.profile_keyboard)
                    try:
                        await bot.send_message(referrer_id, config.NEW_REF_MESSAGE)
                    except:
                        pass
                else:
                    await bot.send_message(message.from_user.id, config.SELF_REF_MESSAGE)
            else:
                db.add_user(message.from_user.id)
                await bot.send_message(message.from_user.id, config.WELCOME_MESSAGE,
                                       reply_markup=markups.profile_keyboard)
        else:
            await bot.send_message(message.from_user.id, config.TAKED_PART_MESSAGE,
                                   reply_markup=markups.profile_keyboard)
    else:
        await bot.send_message(message.from_user.id, config.NOT_SUB_MESSAGE,
                               reply_markup=markups.show_channels())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
