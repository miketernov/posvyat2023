from aiogram.dispatcher import FSMContext
from bot_const import *
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from bot_db import check_if_user, add_user, delete_user, get_username
from aiogram.types import ReplyKeyboardRemove
from main import get_student_info, check_if_in, check_if_in_org, get_org_schedule, get_my_schedule, check_if_in_tags
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import asyncio
import gspread as gs
import pandas as pd

API_TOKEN = token

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
)


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class MyDialog(StatesGroup):
    waiting_for_student_fi = State()
    waiting_for_org_f = State()

kb1 = [
        [types.KeyboardButton(text="Посмотреть мое расписание")],
        [types.KeyboardButton(text="Посмотреть данные участника")],
        [types.KeyboardButton(text="Посмотреть расписание орга")],
        [types.KeyboardButton(text="Отключить рассылку")]
    ]

kb2 = [
        [types.KeyboardButton(text="Подключить рассылку")]
    ]

kb3 = [
        [types.KeyboardButton(text="Вернуться в меню")]
    ]


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb2, resize_keyboard=True)
    await message.answer(start_mes, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Подключить рассылку")
async def send_on(message: types.Message):
    id = message.from_user.id
    username = message.from_user.username
    k = check_if_user(id)
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    if k != 0:
        await message.answer(already_in, reply_markup=keyboard)
    else:
        add_user(id, username)
        await message.answer(send_on_const, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Посмотреть мое расписание")
async def send_on(message: types.Message):
    # username = message.from_user.username
    username = "dmsysoev"
    result = get_my_schedule(username)
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    await message.answer(result, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Посмотреть расписание орга")
async def send_on(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb3, resize_keyboard=True)
    await MyDialog.waiting_for_org_f.set()
    await message.answer("Введите фамилию:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Посмотреть данные участника")
async def send_on(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb3, resize_keyboard=True)
    await MyDialog.waiting_for_student_fi.set()
    await message.answer("Введите фамилию и имя:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Вернуться в меню", state=MyDialog.waiting_for_student_fi)
async def process_back_button(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    await state.finish()
    return await message.answer(text="Вы вернулись в меню!", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Вернуться в меню", state=MyDialog.waiting_for_org_f)
async def process_back_button(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    await state.finish()
    return await message.answer(text="Вы вернулись в меню!", reply_markup=keyboard)


@dp.message_handler(lambda message: check_if_in_org(message.text) is False, state=MyDialog.waiting_for_org_f)
async def process_fio_invalid(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb3, resize_keyboard=True)
    return await message.reply("Данные введены неверно, либо данного человека нет с нами! Попробуйте еще раз или вернитесь в меню!", reply_markup=keyboard)


@dp.message_handler(lambda message: check_if_in(message.text) is True, state=MyDialog.waiting_for_student_fi)
async def process_fio_invalid(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb3, resize_keyboard=True)
    return await message.reply("Данные введены неверно, либо данного человека нет в списке! Попробуйте еще раз или вернитесь в меню!", reply_markup=keyboard)


@dp.message_handler(state=MyDialog.waiting_for_student_fi)
async def send_student_info(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.text)
    async with state.proxy() as data:
        data['answer'] = message.text
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    pre_res = data['answer']
    result = get_student_info(pre_res)
    await message.answer(result,
                         reply_markup=keyboard)
    await state.finish()


@dp.message_handler(state=MyDialog.waiting_for_org_f)
async def send_student_info(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.text)
    async with state.proxy() as data:
        data['answer'] = message.text
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    pre_res = data['answer']
    result = get_org_schedule(pre_res)
    await message.answer(result, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(lambda message: message.text == "Отключить рассылку")
async def send_on(message: types.Message):
    id = message.from_user.id
    k = check_if_user(id)
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb2, resize_keyboard=True)
    if k == 0:
        await message.answer(not_send_on, reply_markup=keyboard)
    else:
        delete_user(id)
        await message.answer(send_off, reply_markup=keyboard)


@dp.message_handler()
async def some_text(message: types.Message):
    id = message.from_user.id
    k = check_if_user(id)
    if k == 0:
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb2, resize_keyboard=True)
        await message.answer(confuse_mes_1, reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
        await message.answer(confuse_mes_2, reply_markup=keyboard)


async def send_on_schedule():
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb1, resize_keyboard=True)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('select userid from users')
    user_list = []
    for user in cursor:
        user_list.append(user[0])
    cursor.close()
    conn.close()
    for userid in user_list:
        username = get_username(userid)
        result = get_my_schedule(username)
        await bot.send_message(chat_id=userid, text=result, reply_markup=keyboard)


scheduler = AsyncIOScheduler()
scheduler.add_job(send_on_schedule, trigger='cron', hour=', '.join(map(str, send_hours)), minute=', '.join(map(str, send_mins)))
scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)