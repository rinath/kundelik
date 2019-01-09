
import kundelik
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint

class Chat:
	def __init__(self, bot, chat_id):
		self.bot = bot
		self.chat_id = chat_id
		self.message_type = 0
		self.kundelik = kundelik.Kundelik()
	def on_command_received(self, text):
		ask_credentials = ['start', 'grades', 'homework']
		if text == 'start':
			self.send_message(u'я бот kundelik.kz, мои основные команды:\n/grades посмотреть оценки\n/homework посмотреть домашнее задание\n/exit выйти из аккаунта')
		if text in ask_credentials:
			if not self.kundelik.is_signed_in():
				self.send_message(u'Нужен логин и пароль вашего аккаунта из kundelik.kz')
				self.send_message(u'Логин:')
				self.message_type = 1
			elif text == 'grades':
				self.bot.send_message(self.chat_id, self.kundelik.retrieve_grades(), parse_mode='HTML')
			elif text == 'homework':
				self.send_homework_message(1)
		elif text == 'debug':
			#self.send_message(json.dumps(self.serialize()))
			self.send_message(self.login + ':' + self.password)
		elif text == 'exit':
			self.send_message(u'Вы вышли из аккаунта, чтобы зайти опять напишите команду /start')
			self.kundelik.sign_out()
		else:
			self.send_message(u'Неопознанная команда')
	def on_message_received(self, message):
		if self.message_type == 0:
			self.send_message(u'Напишите комадну /start чтобы начать')
		elif self.message_type == 1:
			self.send_message(u'Пароль:')
			self.kundelik.set_login(message.text)
			self.message_type = 2
		elif self.message_type == 2:
			self.kundelik.set_password(message.text)
			self.kundelik.sign_in()
			if self.kundelik.is_signed_in():
				self.send_message(u'Теперь вы можете отправить команды /grades или /homework')
				self.message_type = 0
			else:
				self.send_message(u'Логин или пароль неверен')
				self.send_message(u'Логин:')
				self.message_type = 1
	def on_callback_received(self, callback):
		commands = callback.data.split()
		print('len(commands):', len(commands))
		if len(commands) > 1 and commands[0] == 'hw':
			print('homework callback received with parameter:', commands[1])
			self.send_homework_message(int(commands[1]), callback)
	def send_homework_message(self, page_number, callback=None):
		homework = self.kundelik.retrieve_homework(page_number)
		markup = InlineKeyboardMarkup()
		st = ''
		buttons = []
		for button in homework['buttons']:
			buttons.append(InlineKeyboardButton(button, callback_data='hw ' + button))
			st += button + ', '
		markup.add(*tuple(buttons))
		if callback:
			self.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
				text=homework['text'], parse_mode='HTML', reply_markup=markup)
		else:
			self.bot.send_message(self.chat_id, homework['text'], parse_mode='HTML', reply_markup=markup)
	def debug_homework(self, page_number):
		reply_markup = []
		pages = 5
		if page_number > 1:
			reply_markup.append(str(page_number - 1))
		if page_number < pages:
			reply_markup.append(str(page_number + 1))
		return {'text':'text: ' + str(page_number), 'buttons':reply_markup}
	def send_message(self, text):
		self.bot.send_message(self.chat_id, text)
	def serialize(self):
		return {
			'message_type' : self.message_type,
			'kundelik' : self.kundelik.serialize()
		}
	def deserialize(self, dic):
		self.message_type = dic['message_type']
		self.kundelik.deserialize(dic['kundelik'])
		return self

bot = telebot.TeleBot('618183139:AAHfHlECjDyxIFl7bGZgoWrP3cIiPmlme5o')
dbfilename = 'db.json'
chats = {}

def load_database():
	try:
		with open(dbfilename, 'r') as f:
			db = json.loads(f.read())
			for chat_id in db:
				chat = Chat(bot, chat_id)
				pprint(db[chat_id])
				chats[chat_id] = chat.deserialize(db[chat_id])
			print('chats len:', len(chats))
	except IOError:
		print('db.json does not exist, nothing is loaded')

def update_database():
	db = {}
	for chat_id in chats:
		db[chat_id] = chats[chat_id].serialize()
	with open(dbfilename, 'w') as f:
		json.dump(db, f)
		print(len(db), 'items dumped')

load_database()

@bot.message_handler(regexp='/\w+') # any commands
def commands(message):
	chat_id = str(message.chat.id)
	if chat_id not in chats:
		chats[chat_id] = Chat(bot, chat_id)
	chats[chat_id].on_command_received(message.text[1:])

@bot.message_handler(content_types=['text'])
def messages(message):
	chat_id = str(message.chat.id)
	if chat_id not in chats:
		chats[chat_id] = Chat(bot, chat_id)
	chats[chat_id].on_message_received(message)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
	chat_id = str(call.message.chat.id)
	if chat_id not in chats:
		chats[chat_id] = Chat(bot, chat_id)
	chats[chat_id].on_callback_received(call)

try:
	print('please wait. signing in to all accounts...')
	bot.polling()
except:
	pass

update_database()
