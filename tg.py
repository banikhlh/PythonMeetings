from telebot import types, TeleBot
from defs import login, logout, user, profile, delete_user, meeting, delete_meeting, get_data_from_db, get_my_data_from_db, give_admin_root, take_admin_root, get_admins, create_room, get_room_data_from_db, online_offline, owner_check, admin_check, get_max_room_id, delete_room, open_connect
import config


bot = TeleBot(config.token)


user_data = {}
meeting_data = {}
room_data = {}


# MENU / START


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn1 = types.InlineKeyboardButton(text='Register', callback_data='register')
    btn2 = types.InlineKeyboardButton(text='Login', callback_data='login')
    btn3= types.InlineKeyboardButton(text='Meetings', callback_data='meetings')

    markup.add(btn1, btn2, btn3)

    text = f'Choose:'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Menu')
def menu_message(message):
    username = message.chat.username
    a = online_offline(username)

    markup = types.InlineKeyboardMarkup()

    if not admin_check(username) and a == 'online':
        markup.add(
            types.InlineKeyboardButton(text='Create meeting', callback_data='create_meeting'),
            types.InlineKeyboardButton(text='Meetings', callback_data='meetings'),
            types.InlineKeyboardButton(text='Profile', callback_data='profile'),
            types.InlineKeyboardButton(text='Admins', callback_data='admins'),
            types.InlineKeyboardButton(text='Admin tools', callback_data='admin_tools'),
            types.InlineKeyboardButton(text='Rooms', callback_data='rooms')
        )
    elif a == 'online':
        markup.add(
            types.InlineKeyboardButton(text='Create meeting', callback_data='create_meeting'),
            types.InlineKeyboardButton(text='Meetings', callback_data='meetings'),
            types.InlineKeyboardButton(text='Profile', callback_data='profile'),
            types.InlineKeyboardButton(text='Admins', callback_data='admins'),
            types.InlineKeyboardButton(text='Rooms', callback_data='rooms')
        )
    else:
        markup.add(
            types.InlineKeyboardButton(text='Register', callback_data='register'),
            types.InlineKeyboardButton(text='Login', callback_data='login'),
            types.InlineKeyboardButton(text='Meetings', callback_data='meetings')
        )

    text = 'Choose:'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def callback_menu(call):
    menu_message(call.message)


# PROFILE


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Profile")
def tg_profile(message):
    user_row, username, email = profile(message.chat.username)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text='My Meetings', callback_data='my_meetings'),
        types.InlineKeyboardButton(text='Update user', callback_data='upd_user'),
        types.InlineKeyboardButton(text='Logout', callback_data='logout'),
        types.InlineKeyboardButton(text='Delete user', callback_data='del_user'),
        types.InlineKeyboardButton(text='Menu', callback_data='menu')
    )

    text = f'Your profile:\nUsername: {username},\nEmail: {email},\nPassword: ********'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# INLINE BUTTON


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def inline_buttons_rooms(call):
    room_id = int(call.data)
    tg_meetings_in_room(call.message, room_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'register':
        tg_reg(call.message)
    elif call.data == 'login':
        tg_log(call.message)
    elif call.data == 'create_meeting':
        tg_create_meeting(call.message)
    elif call.data == 'upd_user':
        tg_upd_user(call.message)
    elif call.data == 'del_user':
        tg_del_user(call.message)
    elif call.data == 'del_meeting':
        tg_del_meeting(call.message)
    elif call.data == 'upd_meeting':
        tg_upd_meeting(call.message)
    elif call.data == 'rooms':
        tg_rooms(call.message)
    elif call.data == 'meetings':
        tg_meetings(call.message)
    elif call.data == 'my_meetings':
        tg_my_meetings(call.message)
    elif call.data == 'crt_room':
        tg_crt_room(call.message)
    elif call.data == 'del_room':
        tg_del_room(call.message)
    elif call.data == 'admins':
        tg_admins(call.message)
    elif call.data == 'del_user_adm':
        tg_del_user_adm(call.message)
    elif call.data == 'del_meeting_adm':
        tg_del_meeting_adm(call.message)
    elif call.data == 'give_adm':
        tg_admin_gr(call.message)
    elif call.data == 'take_adm':
        tg_admin_tr(call.message)
    elif call.data == 'profile':
        tg_profile(call.message)
    elif call.data == 'logout':
        tg_logout(call.message)
    elif call.data == 'admin_tools':
        tg_admin_panel(call.message)


# ROOMS


@bot.message_handler(regexp="Rooms")
def tg_rooms(message):
    a = get_max_room_id()
    markup = types.InlineKeyboardMarkup()
    for i in a:
        markup.add(types.InlineKeyboardButton(text=f'Room {i[0]}', callback_data=str(i[0])))
    btn_menu = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn_menu)

    text_output = "Rooms:"
    for i in a:
        text_output += f'\nRoom {i[0]}'

    bot.send_message(message.chat.id, text_output, reply_markup=markup)


# MEETINGS => ROOM


def tg_meetings_in_room(message, room_id):
    c = get_room_data_from_db(room_id)

    if not c:
        bot.send_message(message.chat.id, "No meetings found for this room.")
        return
    markup = types.InlineKeyboardMarkup()
    
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)

    text_output = "\n".join([", ".join(map(str, row)) for row in c])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


# MEETINGS


@bot.message_handler(regexp="Meetings")
def tg_meetings(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    rows = get_data_from_db()
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


# MY MEETINGS


@bot.message_handler(regexp="My meetings")
def tg_my_meetings(message):
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton(text='Delete meeting', callback_data='del_meeting')
    btn2 = types.InlineKeyboardButton(text='Update meeting', callback_data='upd_meeting')
    btn3 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1, btn2, btn3)
    rows = get_my_data_from_db(message.chat.username)
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


# ADMINS


@bot.message_handler(regexp="Admins")
def tg_admins(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    rows = get_admins()
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All admins:\n{text_output}', reply_markup=markup) 


# REGISTRATION


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) != 'online' and message.text == "Register")
def tg_reg(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Username:", reply_markup=markup)
    bot.register_next_step_handler(message, get_name_reg)


def get_name_reg(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Email:", reply_markup=markup)
    bot.register_next_step_handler(message, get_email_reg)


def get_email_reg(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_name_reg(message)
        return
    email = message.text
    user_data[message.chat.id]['email'] = email

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_password_reg)


def get_password_reg(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_email_reg(message)
        return
    
    password = message.text
    user_data[message.chat.id]['password'] = password

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Repeat Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_repeat_password_reg)


def get_repeat_password_reg(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_password_reg(message)
        return
    
    repeat_password = message.text
    user_data[message.chat.id]['repeat_password'] = repeat_password 
    password = user_data[message.chat.id]['password']
    nickname = user_data[message.chat.id]['nickname']
    email = user_data[message.chat.id]['email']
    username = message.chat.username
    a, b = user(nickname, email, "", password, repeat_password, username, 'reg')
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)

# LOGIN


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) != 'online' and message.text == "Login")
def tg_log(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Username/Email:", reply_markup=markup)
    bot.register_next_step_handler(message, get_name_log)


def get_name_log(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 
    bot.send_message(message.chat.id, "Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_password_log)


def get_password_log(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        tg_log(message)
        return
    
    password = message.text
    user_data[message.chat.id]['password'] = password 
    nickname = user_data[message.chat.id]['nickname']
    username = message.chat.username
    a, b = login(nickname, password, username)
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# LOGOUT


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Logout")
def tg_logout(message):
    a = message.chat.username
    b, c = logout(a)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, b, reply_markup=markup)


# UPDATE USER


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Update user")
def tg_upd_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Username:", reply_markup=markup)
    bot.register_next_step_handler(message, get_name_uu)


def get_name_uu(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 
    bot.send_message(message.chat.id, "Email:", reply_markup=markup)
    bot.register_next_step_handler(message, get_email_uu)


def get_email_uu(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        tg_upd_user(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    email = message.text
    user_data[message.chat.id]['email'] = email
    bot.send_message(message.chat.id, "Old Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_old_password_uu)


def get_old_password_uu(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_name_uu(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    old_password = message.text
    user_data[message.chat.id]['old_password'] = old_password
    bot.send_message(message.chat.id, "New Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_password_uu)


def get_password_uu(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_email_uu(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    password = message.text
    user_data[message.chat.id]['password'] = password
    bot.send_message(message.chat.id, "Repeat Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_repeat_password_uu)


def get_repeat_password_uu(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_old_password_uu(message)
        return
    
    repeat_password = message.text
    user_data[message.chat.id]['repeat_password'] = repeat_password 
    old_password = user_data[message.chat.id]['old_password']
    password = user_data[message.chat.id]['password']
    nickname = user_data[message.chat.id]['nickname']
    email = user_data[message.chat.id]['email']
    username = message.chat.username
    a, b = user(nickname, email, old_password, password, repeat_password, username, 'upd')
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# DELETE USER


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Delete user")
def tg_del_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Password", reply_markup=markup)
    bot.register_next_step_handler(message, get_password_du)


def get_password_du(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    a = message.text
    b = message.chat.username
    c, d = delete_user(a, b, 'no')
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# CREATE MEETING


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Create meeting")
def tg_create_meeting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Meetings`s name:", reply_markup=markup)
    bot.register_next_step_handler(message, get_name_cm)


def get_name_cm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    name = message.text
    meeting_data[message.chat.id] = {'name': name} 
    bot.send_message(message.chat.id, "Members:", reply_markup=markup)
    bot.register_next_step_handler(message, get_members_cm)


def get_members_cm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        tg_create_meeting(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    members = message.text
    meeting_data[message.chat.id]['members'] = members
    bot.send_message(message.chat.id, "Start Datetime(YYYY-mm-ddTHH:MM):", reply_markup=markup)
    bot.register_next_step_handler(message, get_dts_cm)


def get_dts_cm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_name_cm(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    dt_start = message.text
    meeting_data[message.chat.id]['dt_start'] = dt_start
    bot.send_message(message.chat.id, "End Datetime(YYYY-mm-ddTHH:MM):", reply_markup=markup)
    bot.register_next_step_handler(message, get_dte_cm)


def get_dte_cm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_members_cm(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    dt_end = message.text
    meeting_data[message.chat.id]['dt_end'] = dt_end
    bot.send_message(message.chat.id, "Number of room:", reply_markup=markup)
    bot.register_next_step_handler(message, get_room_cm)


def get_room_cm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_dts_cm(message)
        return
    
    room = message.text
    meeting_data[message.chat.id]['room'] = room
    dt_end = meeting_data[message.chat.id]['dt_end']
    dt_start = meeting_data[message.chat.id]['dt_start']
    name = meeting_data[message.chat.id]['name']
    members = meeting_data[message.chat.id]['members']
    username = message.chat.username
    a, b = meeting('', name, members, dt_start, dt_end, room, username, 'crt')
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# UPDATE MEETING


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Update meeting")
def tg_upd_meeting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Id meeting:", reply_markup=markup)
    bot.register_next_step_handler(message, get_id_um)


def get_id_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    meeting_data[message.chat.id] = {'id_meeting': message.text}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "New name:", reply_markup=markup)
    bot.register_next_step_handler(message, get_new_name_um)


def get_new_name_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        tg_upd_meeting(message)
        return

    meeting_data[message.chat.id]['new_name'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Members:", reply_markup=markup)
    bot.register_next_step_handler(message, get_members_um)


def get_members_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_id_um(message)
        return

    meeting_data[message.chat.id]['members'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Start Datetime (YYYY-mm-ddTHH:MM):", reply_markup=markup)
    bot.register_next_step_handler(message, get_dts_um)


def get_dts_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_new_name_um(message)
        return

    meeting_data[message.chat.id]['dt_start'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "End Datetime (YYYY-mm-ddTHH:MM):", reply_markup=markup)
    bot.register_next_step_handler(message, get_dte_um)


def get_dte_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_members_um(message)
        return

    meeting_data[message.chat.id]['dt_end'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Number of room:", reply_markup=markup)
    bot.register_next_step_handler(message, get_room_um)


def get_room_um(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        get_dts_um(message)
        return

    room = message.text
    meeting_data[message.chat.id]['room'] = room
    dt_end = meeting_data[message.chat.id]['dt_end']
    dt_start = meeting_data[message.chat.id]['dt_start']
    id_meeting = meeting_data[message.chat.id]['id_meeting']
    new_name = meeting_data[message.chat.id]['new_name']
    members = meeting_data[message.chat.id]['members']
    username = message.chat.username


    a, b = meeting(id_meeting, new_name, members, dt_start, dt_end, room, username, 'upd')
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# DELETE MEETING


@bot.message_handler(func=lambda message: online_offline(message.chat.username) == 'online' and message.text == "Delete meeting")
def tg_del_meeting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Meeting`s id:", reply_markup=markup)
    bot.register_next_step_handler(message, get_id_dm)


def get_id_dm(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    a = message.text
    b = message.chat.username
    c, d = delete_meeting(a, b, 'no')
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# CREATE ROOM


@bot.message_handler(func=lambda message: (not admin_check(message.chat.username)) and message.text == "Create room")
def tg_crt_room(message):
    if not admin_check(message.chat.username):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
        markup.add(btn1)

        text = create_room(message.chat.username)
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
        markup.add(btn1)

        text = 'You not admin :/'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# DELETE ROOM


@bot.message_handler(func=lambda message: (not admin_check(message.chat.username)) and message.text == "Delete room")
def tg_del_room(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "ID:", reply_markup=markup)
    bot.register_next_step_handler(message, get_id_delr)


def get_id_delr(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    btn2 = types.KeyboardButton('Back')
    markup.add(btn1, btn2)
    id = message.text
    room_data[message.chat.id] = {'id': id} 
    bot.send_message(message.chat.id, "Password:", reply_markup=markup)
    bot.register_next_step_handler(message, get_password_log)


def get_password_delr(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    if message.text.lower() == 'back':
        tg_del_room(message)
        return
    
    password = message.text
    user_data[message.chat.id]['password'] = password 
    id = room_data[message.chat.id]['id']
    username = message.chat.username
    a, b = delete_room(id, password, username, 'yes')
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# ADMIN TOOLS


@bot.message_handler(func=lambda message: (not admin_check(message.chat.username)) and message.text == "Admin tools")
def tg_admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    a = online_offline(message.chat.username)
    if (not owner_check(message.chat.username)) and a == 'online':

        btn1 = types.InlineKeyboardButton(text='Delete user (admin)', callback_data='del_user_adm')
        btn2 = types.InlineKeyboardButton(text='Delete meeting (admin)', callback_data='del_meeting_adm')
        btn3 = types.InlineKeyboardButton(text='Give admin root', callback_data='give_adm')
        btn4 = types.InlineKeyboardButton(text='Take admin root', callback_data='take_adm')
        btn5 = types.InlineKeyboardButton(text='Create room', callback_data='crt_room')
        btn6 = types.InlineKeyboardButton(text='Delete room', callback_data='del_room')
        btn7 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        text = f'Choose:'
    elif (not admin_check(message.chat.username)) and a == 'online':
    
        btn1 = types.InlineKeyboardButton(text='Delete user (admin)', callback_data='del_user_adm')
        btn2 = types.InlineKeyboardButton(text='Delete meeting (admin)', callback_data='del_meeting_adm')
        btn3 = types.InlineKeyboardButton(text='Create room', callback_data='crt_room')
        btn4 = types.InlineKeyboardButton(text='Delete room', callback_data='del_room')
        btn5 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        text = f'Choose:'
    else:
        text = 'You not admin :/'
        btn1 = types.KeyboardButton('Menu')
        markup.add(btn1)
    

    bot.send_message(message.chat.id, text, reply_markup=markup)


# GIVE ADMIN ROOT


@bot.message_handler(func=lambda message: (not owner_check(message.chat.username)) and message.text == "Give admin root")
def tg_admin_gr(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Id:", reply_markup=markup)
    bot.register_next_step_handler(message, tg_id_gar)


def tg_id_gar(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    text = message.text
    a = int(text)
    b = message.chat.username
    c, d = give_admin_root(a, b)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# TAKE ADMIN ROOT


@bot.message_handler(func=lambda message: (not owner_check(message.chat.username)) and message.text == "Take admin root")
def tg_admin_tr(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Id:", reply_markup=markup)
    bot.register_next_step_handler(message, tg_id_tar)


def tg_id_tar(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    text = message.text
    a = int(text)
    b = message.chat.username
    c, d = take_admin_root(a, b)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# DELETE USER ADMIN


@bot.message_handler(func=lambda message: (not admin_check(message.chat.username)) and message.text == "Delete user(Admin)")
def tg_del_user_adm(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "User`s id:", reply_markup=markup)
    bot.register_next_step_handler(message, user_da)


def user_da(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    a = message.text
    b = message.chat.username
    c, d = delete_user(a, "", b, "yes")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# DELETE MEETING ADMIN


@bot.message_handler(func=lambda message: (not admin_check(message.chat.username)) and message.text == "Delete meetings(Admin)")
def tg_del_meeting_adm(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Meeting`s id:", reply_markup=markup)
    bot.register_next_step_handler(message, meeting_da)


def meeting_da(message):
    if message.text.lower() == 'menu':
        menu_message(message)
        return
    
    a = message.text
    b = message.chat.username
    c, d = delete_meeting(a, b, "yes")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Menu', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)