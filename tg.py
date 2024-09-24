from telebot import types, TeleBot
from defs import login, logout, user, profile, delete_user, meeting, delete_meeting, open_connect, get_data_from_db, get_my_data_from_db, give_admin_root, take_admin_root, get_admins, create_room, get_room_data_from_db, online_offline, owner_check, admin_check, get_max_room_id, delete_room
import config


bot = TeleBot(config.token)


user_data = {}
meeting_data = {}
room_data = {}


@bot.message_handler(func=lambda message: (not admin_check(message.from_user.username)) and message.text == "Admin tools")
def tg_admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    a = online_offline(message.from_user.username)
    if (not owner_check(message.from_user.username)) and a == 'online':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton('Delete user(Admin)')
        btn2 = types.KeyboardButton('Delete meetings(Admin)')
        btn3 = types.KeyboardButton('Give admin root')
        btn4 = types.KeyboardButton('Take admin root')
        btn5 = types.KeyboardButton('Create room')
        btn6 = types.KeyboardButton('Delete room')
        btn7 = types.KeyboardButton('Menu')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    elif (not admin_check(message.from_user.username)) and a == 'online':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Delete user(Admin)')
        btn2 = types.KeyboardButton('Delete meetings(Admin)')
        btn3 = types.KeyboardButton('Create room')
        btn4 = types.KeyboardButton('Delete room')
        btn5 = types.KeyboardButton('Menu')
        markup.add(btn1, btn2, btn3, btn4, btn5)

    text = f'Choose:'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# Delete user admin


@bot.message_handler(func=lambda message: (not admin_check(message.from_user.username)) and message.text == "Delete user(Admin)")
def tg_delete_user_adm(message):
    bot.send_message(message.chat.id, "User`s id:")
    bot.register_next_step_handler(message, user_da)


def user_da(message):
    a = message.text
    b = message.from_user.username
    c, d = delete_user(a, "", b, "yes")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# Delete meeting admin


@bot.message_handler(func=lambda message: (not admin_check(message.from_user.username)) and message.text == "Delete meetings(Admin)")
def tg_delete_meeting_adm(message):
    bot.send_message(message.chat.id, "Meeting`s id:")
    bot.register_next_step_handler(message, meeting_da)


def meeting_da(message):
    a = message.text
    b = message.from_user.username
    c, d = delete_meeting(a, b, "yes")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


@bot.message_handler(regexp="Rooms")
def tg_rooms(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    a = get_max_room_id()
    text_output = f"Rooms:"
    for i in a:
        b = f'\nRoom {i[0]}'
        text_output = text_output + b
    print(a)
    bot.send_message(message.chat.id, text_output, reply_markup=markup)


@bot.message_handler(regexp="Meetings")
def tg_meetings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    rows = get_data_from_db()
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


@bot.message_handler(regexp="Admins")
def tg_admins(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    rows = get_admins()
    text_output = "\n".join([", ".join(map(str, row)) for row in rows])
    bot.send_message(message.chat.id, f'All meetings:\n{text_output}', reply_markup=markup)


@bot.message_handler(regexp="My meetings")
def tg_my_meetings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Delete meeting')
    btn2 = types.KeyboardButton('Update meeting')
    btn3 = types.KeyboardButton('Menu')
    markup.add(btn1, btn2, btn3)
    rows = get_my_data_from_db()
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
    bot.register_next_step_handler(message, get_repeat_password_reg)


def get_repeat_password_reg(message):
    password = message.text
    user_data[message.chat.id]['password'] = password
    bot.send_message(message.chat.id, "Repeat Password:")
    bot.register_next_step_handler(message, get_password_reg)


def get_password_reg(message):
    repeat_password = message.text
    user_data[message.chat.id]['repeat_password'] = repeat_password 
    password = user_data[message.chat.id]['password']
    nickname = user_data[message.chat.id]['nickname']
    email = user_data[message.chat.id]['email']
    username = message.from_user.username
    a, b = user(nickname, email, "", password, repeat_password, username, 'reg')
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
    b, c = logout(a)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, b, reply_markup=markup)


# Update user


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Update user")
def tg_update_user(message):
    bot.send_message(message.chat.id, "Username:")
    bot.register_next_step_handler(message, get_nickname_uu)


def get_nickname_uu(message):
    nickname = message.text
    user_data[message.chat.id] = {'nickname': nickname} 
    bot.send_message(message.chat.id, "Email:")
    bot.register_next_step_handler(message, get_email_uu)


def get_email_uu(message):
    email = message.text
    user_data[message.chat.id]['email'] = email
    bot.send_message(message.chat.id, "Old Password:")
    bot.register_next_step_handler(message, get_old_password_uu)


def get_old_password_uu(message):
    old_password = message.text
    user_data[message.chat.id]['old_password'] = old_password
    bot.send_message(message.chat.id, "New Password:")
    bot.register_next_step_handler(message, get_repeat_password_uu)


def get_repeat_password_uu(message):
    password = message.text
    user_data[message.chat.id]['password'] = password
    bot.send_message(message.chat.id, "Repeat Password:")
    bot.register_next_step_handler(message, get_password_uu)


def get_password_uu(message):
    repeat_password = message.text
    user_data[message.chat.id]['repeat_password'] = repeat_password 
    old_password = user_data[message.chat.id]['old_password']
    password = user_data[message.chat.id]['password']
    nickname = user_data[message.chat.id]['nickname']
    email = user_data[message.chat.id]['email']
    username = message.from_user.username
    a, b = user(nickname, email, old_password, password, repeat_password, username, 'upd')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Delete user


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Delete user")
def tg_delete_user(message):
    bot.send_message(message.chat.id, "Password")
    bot.register_next_step_handler(message, user_du)


def user_du(message):
    a = message.text
    b = message.from_user.username
    c, d = delete_user(a, b)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# Create meeting


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Create meeting")
def tg_create_meeting(message):
    bot.send_message(message.chat.id, "Meetings`s name:")
    bot.register_next_step_handler(message, get_name_cm)


def get_name_cm(message):
    name = message.text
    meeting_data[message.chat.id] = {'name': name} 
    bot.send_message(message.chat.id, "Members:")
    bot.register_next_step_handler(message, get_members_cm)


def get_members_cm(message):
    members = message.text
    meeting_data[message.chat.id]['members'] = members
    bot.send_message(message.chat.id, "Start Datetime(YYYY-mm-ddTHH:MM):")
    bot.register_next_step_handler(message, get_dt_cm)


def get_dt_cm(message):
    dt_start = message.text
    meeting_data[message.chat.id]['dt_start'] = dt_start
    bot.send_message(message.chat.id, "End Datetime(YYYY-mm-ddTHH:MM):")
    bot.register_next_step_handler(message, get_room_cm)


def get_room_cm(message):
    dt_end = message.text
    meeting_data[message.chat.id]['dt_end'] = dt_end
    bot.send_message(message.chat.id, "Number of room:")
    bot.register_next_step_handler(message, meet_cm)


def meet_cm(message):
    room = message.text
    meeting_data[message.chat.id]['room'] = room
    dt_end = meeting_data[message.chat.id]['dt_end']
    dt_start = meeting_data[message.chat.id]['dt_start']
    name = meeting_data[message.chat.id]['name']
    members = meeting_data[message.chat.id]['members']
    username = message.from_user.username
    a, b = meeting('', name, members, dt_start, dt_end, room, username, 'crt')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Delete meeting


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Delete meeting")
def tg_delete_meeting(message):
    bot.send_message(message.chat.id, "Meeting`s id:")
    bot.register_next_step_handler(message, meet_dm)


def meet_dm(message):
    a = message.text
    b = message.from_user.username
    c, d = delete_meeting(a, b)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# Update meeting


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Update meeting")
def tg_update_meeting(message):
    bot.send_message(message.chat.id, "Id meeting:")
    bot.register_next_step_handler(message, get_id_meeting_um)


def get_id_meeting_um(message):
    id_meeting = message.text
    meeting_data[message.chat.id] = {'id_meeting': id_meeting} 
    bot.send_message(message.chat.id, "New name:")
    bot.register_next_step_handler(message, get_new_name_um)


def get_new_name_um(message):
    new_name = message.text
    meeting_data[message.chat.id]['new_name'] = new_name
    bot.send_message(message.chat.id, "Members:")
    bot.register_next_step_handler(message, get_members_um)


def get_members_um(message):
    members = message.text
    meeting_data[message.chat.id]['members'] = members
    bot.send_message(message.chat.id, "Start Datetime(YYYY-mm-ddTHH:MM):")
    bot.register_next_step_handler(message, get_dt_um)


def get_dt_um(message):
    dt_start = message.text
    meeting_data[message.chat.id]['dt_start'] = dt_start
    bot.send_message(message.chat.id, "End Datetime(YYYY-mm-ddTHH:MM):")
    bot.register_next_step_handler(message, get_room_um)


def get_room_um(message):
    dt_end = message.text
    meeting_data[message.chat.id]['dt_end'] = dt_end
    bot.send_message(message.chat.id, "Number of room:")
    bot.register_next_step_handler(message, meet_cm)


def meet_um(message):
    room = message.text
    meeting_data[message.chat.id]['room'] = room
    dt_end = meeting_data[message.chat.id]['dt_end']
    dt_start = meeting_data[message.chat.id]['dt_start']
    id_meeting = meeting_data[message.chat.id]['id_meeting']
    new_name = meeting_data[message.chat.id]['new_name']
    members = meeting_data[message.chat.id]['members']
    username = message.from_user.username
    a, b = meeting(id_meeting, new_name, members, dt_start, dt_end, room, username, 'upd')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)


# Profile


@bot.message_handler(func=lambda message: online_offline(message.from_user.username) == 'online' and message.text == "Profile")
def menu_message(message):
    user_row, username, email = profile(message.from_user.username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Update user')
    btn2 = types.KeyboardButton('Logout')
    btn3 = types.KeyboardButton('Delete user')
    btn4 = types.KeyboardButton('Menu')
    markup.add(btn1, btn2, btn3, btn4)

    text = f'Your profile:\nUsername: {username},\nEmail: {email},\nPassword: ********'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# Give admin root


@bot.message_handler(func=lambda message: (not owner_check(message.from_user.username)) and message.text == "Give admin root")
def tg_admin_gr(message):
    bot.send_message(message.chat.id, "Id:")
    bot.register_next_step_handler(message, tg_id_gar)


def tg_id_gar(message):
    text = message.text
    a = int(text)
    b = message.from_user.username
    c, d = give_admin_root(a, b)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


# Take admin root


@bot.message_handler(func=lambda message: (not owner_check(message.from_user.username)) and message.text == "Take admin root")
def tg_admin_tr(message):
    bot.send_message(message.chat.id, "Id:")
    bot.register_next_step_handler(message, tg_id_tar)


def tg_id_tar(message):
    text = message.text
    a = int(text)
    b = message.from_user.username
    c, d = take_admin_root(a, b)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, c, reply_markup=markup)


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
    if (not admin_check(message.from_user.username)) and a == 'online':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Create meeting')
        btn2 = types.KeyboardButton('Meetings')
        btn3 = types.KeyboardButton('My meetings')
        btn4 = types.KeyboardButton('Profile')
        btn5 = types.KeyboardButton('Admins')
        btn6 = types.KeyboardButton('Admin tools')
        btn7 = types.KeyboardButton('Rooms')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    elif a == 'online':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Create meeting')
        btn2 = types.KeyboardButton('Meetings')
        btn3 = types.KeyboardButton('My meetings')
        btn4 = types.KeyboardButton('Profile')
        btn5 = types.KeyboardButton('Admins')
        btn6 = types.KeyboardButton('Rooms')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        btn1 = types.KeyboardButton('Register')
        btn2 = types.KeyboardButton('Login')
        btn3 = types.KeyboardButton('Meetings')
        markup.add(btn1, btn2, btn3)

    text = f'Choose:'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: (not admin_check(message.from_user.username)) and message.text == "Create room")
def tg_crt_room(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)

    text = create_room(message.from_user.username)

    bot.send_message(message.chat.id, text, reply_markup=markup)


# Delete room


@bot.message_handler(func=lambda message: (not admin_check(message.from_user.username)) and message.text == "Delete room")
def tg_del_room(message):
    bot.send_message(message.chat.id, "ID:")
    bot.register_next_step_handler(message, get_id_delr)


def get_id_delr(message):
    id = message.text
    room_data[message.chat.id] = {'id': id} 
    bot.send_message(message.chat.id, "Password:")
    bot.register_next_step_handler(message, get_password_log)


def get_password_delr(message):
    password = message.text
    user_data[message.chat.id]['password'] = password 
    id = room_data[message.chat.id]['id']
    username = message.from_user.username
    a, b = delete_room(id, password, username, 'yes')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, a, reply_markup=markup)