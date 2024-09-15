from telebot import types, TeleBot
from defs import logout, login, register, create_meeting, online_offline, users_txt, get_data_from_db
import config


bot = TeleBot(config.token)


user_data = {}
meeting_data = {}


@bot.message_handler(regexp="Meetings")
def tg_meetings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    rows = get_data_from_db()
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


# Register


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) != 'online' and message.text == "Register")
def tg_register(message):
    bot.send_message(message.chat.id, "Username:")
    bot.register_next_step_handler(message, get_nickname_reg)


def get_nickname_reg(message):
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 
    bot.send_message(message.chat.id, "Email:")
    bot.register_next_step_handler(message, get_email_reg)


def get_email_reg(message):
    email = message.text
    user_data[message.chat.id]['email'] = email
    bot.send_message(message.chat.id, "Password:")
    bot.register_next_step_handler(message, get_password_reg)


def get_password_reg(message):
    password = message.text
    user_data[message.chat.id]['password'] = password 
    nickname = user_data[message.chat.id]['nickname']
    email = user_data[message.chat.id]['email']
    username = message.from_user.username
    a, b = register(nickname, password, email, username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Login


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) != 'online' and message.text == "Login")
def tg_login(message):
    bot.send_message(message.chat.id, "Username/Email:")
    bot.register_next_step_handler(message, get_nickname_log)


def get_nickname_log(message):
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 
    bot.send_message(message.chat.id, "Password:")
    bot.register_next_step_handler(message, get_password_log)


def get_password_log(message):
    password = message.text
    user_data[message.chat.id]['password'] = password 
    nickname = user_data[message.chat.id]['nickname']
    username = message.from_user.username
    a, b = login(nickname, password, username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Logout


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Logout")
def tg_logout(message):
    a = message.from_user.username
    logout(a)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)

    text = f'You logouted!'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# Create meeting


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Create meeting")
def tg_create_meeting(message):
    bot.send_message(message.chat.id, "Meetings`s name:")
    bot.register_next_step_handler(message, get_name_crm)


def get_name_crm(message):
    name = message.text
    meeting_data[message.chat.id] = {'name': name} 
    bot.send_message(message.chat.id, "Members:")
    bot.register_next_step_handler(message, get_members_crm)


def get_members_crm(message):
    members = message.text
    meeting_data[message.chat.id]['members'] = members
    bot.send_message(message.chat.id, "Datetime(YYYY-mm-ddTHH:MM):")
    bot.register_next_step_handler(message, meet_crm)


def meet_crm(message):
    dt = message.text
    meeting_data[message.chat.id]['dt'] = dt
    name = meeting_data[message.chat.id]['name']
    members = meeting_data[message.chat.id]['members']
    username = message.from_user.username
    a, b = create_meeting(name, members, dt, username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Menu


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn1 = types.KeyboardButton('Register')
    btn2 = types.KeyboardButton('Login')
    btn3 = types.KeyboardButton('Meetings')

    markup.add(btn1, btn2, btn3)

    text = f'Привет {message.from_user.full_name}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Menu')
def menu_message(message):
    a = online_offline(message.from_user.username)
    if a == 'online':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Create meeting')
        btn2 = types.KeyboardButton('Logout')
        btn3 = types.KeyboardButton('Meetings')

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Register')
        btn2 = types.KeyboardButton('Login')
        btn3 = types.KeyboardButton('Meetings')

    markup.add(btn1, btn2, btn3)

    text = f'Choose:'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_id_admin and message.text == "Console")
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Users')
    markup.add(btn1, btn2)
    text = f'Admin-menu'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_id_admin and message.text == "Users")
def menu_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)

    text = f'All users:\n{users_txt()}'

    bot.send_message(message.chat.id, text, reply_markup=markup)
