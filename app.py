# -*- coding: utf-8 -*-

# AIOGRAM
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import Throttled
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, reply_keyboard
from aiogram.utils import executor
import aiogram.utils
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from sqlalchemy.sql.operators import op
from multiprocessing.pool import ThreadPool
import requests
from requests import HTTPError

# DB models
from models import db_session
from models.users import User

# Admin panel
import threading
def web():
    import web
x = threading.Thread(target=web)
#x.start()

# Logging
from scripts.checks import async_print_log, print_log

# Browser
from scripts.browser import browser
#browser('https://google.com', 1920, 1080, 'console.log("test");', True)

# ...
import datetime, json

db_session.global_init('database.db')

f = open(f'settings.json', "r")
settings = json.loads(f.read())
bot_token = settings["token"] # token

bot = Bot(token=bot_token)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class States(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()

async def anti_flood(*args, **kwargs):
    m = args[0]
    await m.answer("👮 Слишком много запросов, просим подождать!")

# /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
	session = db_session.create_session()
	iduser = message.from_user.id
	user_all = session.query(User).all()
	T = True
	for all in user_all:
		if all.id == iduser:
			T = False

	if T == True:
		# добавить нового юзера
		session = db_session.create_session()
		name = message.from_user.first_name
		url = message.from_user.username
		iduser = message.from_user.id
		fullname = '-'
		if message.from_user.last_name != None:
			fullname = message.from_user.last_name

		username = '-'
		if message.from_user.username != None:
			username = f'@{message.from_user.username}'
        
		now = datetime.datetime.now()
		user = User(
			id=iduser,
			name=name,
            fullname=fullname,
			data='[{}]',
            username=username,
            work=now.strftime("%d-%m-%Y %H:%M")
		)
		session.add(user)
		session.commit()
		await bot.send_photo(message.chat.id, photo=open('md/1.gif', 'rb'), caption='''👋 Здравствуй, я - бот для тестирования веба, в мой возможности вхоит открытие страниц с определёнными параметрами настраиваемые вами, и в конечном результате вы получаете скриншот страницы!\n🌐 Введи ссылку на страницу, и мы начнём:''', parse_mode="HTML")
		await async_print_log(f"New user ID: {iduser} {name}", 'INFO', 'BOT')
	else:
		await bot.send_photo(message.chat.id, photo=open('md/1.gif', 'rb'), caption='👋 Здравствуй, я - бот для тестирования веба, в мой возможности вхоит открытие страниц с определёнными параметрами настраиваемые вами, и в конечном результате вы получаете скриншот страницы!\n🌐 Введи ссылку на страницу, и мы начнём:')

@dp.message_handler(content_types=["text"])
@dp.throttled(anti_flood, rate=10)
async def check(message: types.Message):
	try:
		if message.text:
			pk = types.KeyboardButton('1920x1080')
			phone = types.KeyboardButton('360x740')
			main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
			main_kb.add(pk)   
			main_kb.add(phone) 
			await bot.send_message(message.chat.id, '🎚 Введите ширину и высоту в формате `1920x1080`:', reply_markup=main_kb)

			session = db_session.create_session()
			user_all = session.query(User).all()

			for user in user_all:
				if user.id == message.from_user.id:
					dict_json = {
						'url': '',
						'width': '',
						'height': '',
						'script': '',
						'fullpage': ''
					}
					dict_json['url'] = message.text
					user.data = json.dumps(dict_json, ensure_ascii=False)
			session.commit()
			state = dp.current_state(user=message.from_user.id)
			await state.set_state(States.all()[0])
	except BaseException as e:
		await bot.send_message(1218845111, 'В системе ошибка...\n<code>' + str(e) + '</code>', parse_mode='html')
		await bot.send_message(message.chat.id, 'Упс, ошибка...')
		await async_print_log(f"Error: {e}", 'ERROR', 'BOT')

@dp.message_handler(state=States.STATE_0)
async def state_case_met1(message: types.Message):
	session = db_session.create_session()
	user_all = session.query(User).all()
	console = types.KeyboardButton('console.log("test");')
	alert = types.KeyboardButton('alert("test");')
	main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
	main_kb.add(console)   
	main_kb.add(alert) 
	size = message.text.split('x')
	try:
		size = size.split('х')
	except:
		pass
	width = size[0]
	height = size[1]
	for user in user_all:
		if user.id == message.from_user.id:
			dict_json = json.loads(user.data)
			dict_json['width'] = width
			dict_json['height'] = height
			user.data = json.dumps(dict_json, ensure_ascii=False)
	session.commit()
	await bot.send_message(message.chat.id, '☕️ Введите скрипт js, он будет выполнен:', reply_markup=main_kb)
	state = dp.current_state(user=message.from_user.id)
	await state.set_state(States.all()[1])

	#state = dp.current_state(user=message.from_user.id)
	#await state.reset_state()

@dp.message_handler(state=States.STATE_1)
async def state_case_met2(message: types.Message):
	full = types.KeyboardButton('Скрин всей страницы')
	look = types.KeyboardButton('Скрин видимой части')
	main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
	main_kb.add(full)   
	main_kb.add(look) 
	session = db_session.create_session()
	user_all = session.query(User).all()
	script = message.text
	for user in user_all:
		if user.id == message.from_user.id:
			dict_json = json.loads(user.data)
			dict_json['script'] = script
			user.data = json.dumps(dict_json, ensure_ascii=False)
	await bot.send_message(message.chat.id, '📑 И последнее, выберите:', reply_markup=main_kb)
	session.commit()
	state = dp.current_state(user=message.from_user.id)
	await state.set_state(States.all()[2])

	#state = dp.current_state(user=message.from_user.id)
	#await state.reset_state()

@dp.message_handler(state=States.STATE_2)
async def state_case_met2(message: types.Message):
	res = False
	if message.text == 'Скрин всей страницы':
		res = True
	session = db_session.create_session()
	user_all = session.query(User).all()
	for user in user_all:
		if user.id == message.from_user.id:
			dict_json = json.loads(user.data)
			dict_json['fullpage'] = res
			user.data = json.dumps(dict_json, ensure_ascii=False)
	await bot.send_message(message.chat.id, '🧮 В процессе, в среднем это длится 6 секунд...')

	pool = ThreadPool(processes=1)
	result = pool.apply_async(browser, (dict_json['url'], dict_json['width'], dict_json['height'], dict_json['script'], dict_json['fullpage']))
	result = result.get()
	log = ''
	log1 = ''
	URL = "https://nekobin.com"
	post = "https://nekobin.com/api/documents"
	try:
		paste = requests.post(post, data={"content": result['script']})
		log = f"{URL}/{paste.json()['result']['key']}"
	except Exception as e:
		log = f"https://nekobin.com/qocosolaba"

	try:
		paste = requests.post(post, data={"content": result['logs']})
		log1 = f"{URL}/{paste.json()['result']['key']}"
	except Exception as e:
		log1 = f"https://nekobin.com/qocosolaba"
	
	if result['img'] != 'error':
		await bot.send_photo(message.chat.id, photo=open(f"img/{result['img']}.png", 'rb'), caption=f'''<b>🕵️‍♂️ Анализ сайта прошёл успешно:</b>
  <a href="https://developers.google.com/speed/pagespeed/insights/?hl=ru&url={dict_json['url']}">🔬 Анализ LightHouse</a>
  <a href="{log}">💾 Логи сайта</a>
  <a href="{log1}">🧪 Результат выполнения скрипта</a>''', parse_mode='html')
	else:
		await bot.send_photo(message.chat.id, photo=open(f"img/{result['img']}.png", 'rb'), caption=f'''<b>🕵️‍♂️Ошибка анализа сайта, пожалуйста проверьте ссылку на сайт и скрипт!</b>''', parse_mode='html')

	session.commit()
	state = dp.current_state(user=message.from_user.id)
	await state.reset_state()

async def ad_send(text):
	session = db_session.create_session()
	user_all = session.query(User).all()
	have = 0
	try:
		for all in user_all:
			await bot.send_message(all.id, text, parse_mode='HTML')
			have = have + 1
	except Exception:
		pass
	await async_print_log(f"Ad sending {have}!", 'INFO', 'BOT')
	return have

if __name__ == "__main__":
	print_log(f"Bot starting", 'INFO', 'BOT')
	executor.start_polling(dp)
	print_log(f"Bot stoping", 'INFO', 'BOT')