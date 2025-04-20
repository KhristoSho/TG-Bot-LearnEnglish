import random
from managerDB import *
from managerTG import *
from keys import LOGIN_BD, PASSWORD_BD, NAME_BD, HOST, PORT, TOKEN_TG
from telebot import TeleBot, types
from telebot.handler_backends import State, StatesGroup
from managerTG import made_buttons

DB = ManangerDB(LOGIN_BD, PASSWORD_BD, NAME_BD, HOST, PORT)
bot = TeleBot(TOKEN_TG)

DB.create_table()
DB.import_base_words()


class MyState(StatesGroup):
    main_menu_state = State()
    add_word_step1 = State()
    add_word_step2 = State()
    word_EN = State()
    del_word_step1 = State()
    game_start = State()
    game_continue = State()
    game_mode = State()
    goal_word = State()
    right_trans = State()
    incorrect_trans = State()


@bot.message_handler(commands=['start'])
def start_bot(message):

    bot.delete_state(message.from_user.id, message.chat.id)
    userid = message.from_user.id
    if not DB.search_user(userid):
        DB.add_new_user(userid, message.from_user.first_name)

    welcome_message = 'Привет! Я бот для помощи в изучении английского языка🇬🇧.\n\nЯ буду говорить тебе слово, \
а ты должен будешь определить их правильный перевод.\n\nТакже я могу добавлять и удалять для тебя новые слова📝'
    bot.send_message(message.chat.id, welcome_message)

    change_mode_message = 'Выбери режим, в котором хочешь изучать.'
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = made_buttons('Режим\n🇷🇺 -> 🇬🇧', 'Режим\n🇬🇧 -> 🇷🇺', 'Добавить слово📝', 'Удалить слово❌')
    markup.add(*buttons)
    bot.send_message(message.chat.id, change_mode_message, reply_markup=markup)

@bot.message_handler(state=MyState.main_menu_state)
def mode_main_menu(message):

    bot.delete_state(message.from_user.id, message.chat.id)
    message_answ = 'Выбери нужный режим.'
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = made_buttons('Режим\n🇷🇺 -> 🇬🇧', 'Режим\n🇬🇧 -> 🇷🇺', 'Добавить слово📝', 'Удалить слово❌')
    markup.add(*buttons)
    bot.send_message(message.chat.id, message_answ, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def message_hand(message):

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data and 'state' in data:
            return

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id
    text = message.text

    if text == 'Добавить слово📝':

        bot.set_state(userid, MyState.add_word_step1, message.chat.id)

        message_answ = 'Напиши слово на английском языке, которое хочешь добавить в словарь'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = made_buttons('ВЕРНУТЬСЯ В МЕНЮ')
        markup.add(*buttons)
        bot.send_message(message.chat.id, message_answ, reply_markup=markup)
        bot.register_next_step_handler(message, add_word_EN)

    if text == 'Удалить слово❌':

        bot.set_state(userid, MyState.del_word_step1, message.chat.id)

        message_answ = 'Напиши слово на английском языке, которое хочешь удалить из словаря'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = made_buttons('ВЕРНУТЬСЯ В МЕНЮ')
        markup.add(*buttons)
        bot.send_message(message.chat.id, message_answ, reply_markup=markup)
        bot.register_next_step_handler(message, del_word)

    if text == 'Режим\n🇷🇺 -> 🇬🇧' or text == 'Режим\n🇬🇧 -> 🇷🇺':

        bot.set_state(userid, MyState.game_start, message.chat.id)
        with bot.retrieve_data(userid, message.chat.id) as data:
            data['game_mode'] = text
        start_game(message)


@bot.message_handler(state=MyState.add_word_step1)
def add_word_EN(message):

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id
    word = message.text.capitalize()

    if not text_validate(word, mode='add_word_EN'):
        message_answ = 'Пожалуйста, введи одно слово на английском языке без цифр и других символов.'
        bot.send_message(message.chat.id, message_answ)
        bot.register_next_step_handler(message, add_word_EN)
    else:
        word_EN = word
        if not DB.search_word(userid, word_EN):
            with bot.retrieve_data(userid, message.chat.id) as data:
                data['word_EN'] = word_EN
            message_answ = 'Напиши теперь перевод этого слова на русском'
            bot.send_message(message.chat.id, message_answ)
            bot.set_state(userid, MyState.add_word_step2, message.chat.id)
            bot.register_next_step_handler(message, add_word_RU)
        else:
            message_answ = f'Слово "{word_EN}" уже есть в словаре.'
            bot.send_message(message.chat.id, message_answ)
            bot.register_next_step_handler(message, add_word_EN)

@bot.message_handler(state=MyState.add_word_step2)
def add_word_RU(message):

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id
    word = message.text.capitalize()

    if not text_validate(word, mode='add_word_RU'):
        message_answ = 'Пожалуйста, введи одно слово на русском языке без и других символов.'
        bot.send_message(message.chat.id, message_answ)
        bot.register_next_step_handler(message, add_word_RU)
    else:
        with bot.retrieve_data(userid, message.chat.id) as data:
            word_EN = data['word_EN']
        word_RU = word
        DB.add_new_word(userid, word_EN, word_RU)
        message_answ = f'Слово "{word_EN}" с переводом "{word_RU}" успешно добавлены в словарь.'
        bot.send_message(message.chat.id, message_answ)
        message_answ = 'Напиши слово на английском языке, которое хочешь добавить в словарь'
        bot.send_message(message.chat.id, message_answ)
        bot.set_state(message.from_user.id, MyState.add_word_step1, message.chat.id)
        bot.register_next_step_handler(message, add_word_EN)

@bot.message_handler(state=MyState.del_word_step1)
def del_word(message):

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id
    word_EN = message.text

    if not DB.search_word(userid, word_EN):
        message_answ = f'Слово "{word_EN}" не найдено в словаре.'
        bot.send_message(message.chat.id, message_answ)
        bot.register_next_step_handler(message, del_word)
    else:
        DB.del_new_word(userid, word_EN)
        message_answ = f'Слово "{word_EN}" успешно удалено из словаря.'
        bot.send_message(message.chat.id, message_answ)
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)

@bot.message_handler(state=MyState.game_start)
def start_game(message):

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id

    with bot.retrieve_data(userid, message.chat.id) as data:
        mode = data['game_mode']
    if mode == 'Режим\n🇷🇺 -> 🇬🇧':
        goal_word, right_trans, incorrect_trans = DB.get_words_for_game1(userid)
    else:
        goal_word, right_trans, incorrect_trans = DB.get_words_for_game2(userid)

    message_answ = f'Укажи верный перевод слова:\n"{goal_word}"'
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    words = incorrect_trans + [right_trans]
    random.shuffle(words)
    buttons = words + ['Не знаю❌', 'Дальше➡️', 'ВЕРНУТЬСЯ В МЕНЮ']
    buttons = made_buttons(*buttons)
    markup.add(*buttons)
    bot.send_message(message.chat.id, message_answ, reply_markup=markup)

    with bot.retrieve_data(userid, message.chat.id) as data:
        data['goal_word'] = goal_word
        data['right_trans'] = right_trans
        data['incorrect_trans'] = incorrect_trans

    bot.set_state(userid, MyState.game_continue, message.chat.id)
    bot.register_next_step_handler(message, continue_game)

@bot.message_handler(state=MyState.game_continue)
def continue_game(message):

    if message.text == 'ВЕРНУТЬСЯ В МЕНЮ':
        bot.set_state(message.from_user.id, MyState.main_menu_state, message.chat.id)
        mode_main_menu(message)
        return

    userid = message.from_user.id
    text = message.text

    with bot.retrieve_data(userid, message.chat.id) as data:
        right_trans = data['right_trans']

    if text == right_trans:
        message_answ = random.choice(['Молодец✅', 'Правильный ответ!✅', 'Круто✅\nДавай дальше!'])
        bot.set_state(userid, MyState.game_start, message.chat.id)
        bot.send_message(message.chat.id, message_answ)
        start_game(message)

    elif text == 'Не знаю❌':
        message_answ = f'Правильный ответ "{right_trans}"'
        bot.set_state(userid, MyState.game_start, message.chat.id)
        bot.send_message(message.chat.id, message_answ)
        start_game(message)

    elif text == 'Дальше➡️':
        bot.set_state(userid, MyState.game_start, message.chat.id)
        start_game(message)

    else:
        message_answ = random.choice(['К сожалению, неверно❌\nПопробуй еще!', 'Ошибка❌', 'Неверно!\nДавай еще попытку.'])
        bot.send_message(message.chat.id, message_answ)
        bot.register_next_step_handler(message, continue_game)

print("Bot is running!")
bot.infinity_polling(skip_pending=True)
