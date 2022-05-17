import time
import datetime
import telebot
import config
import random
import requests
import pickle
import sys
import os
from bs4 import BeautifulSoup as BS

bot = telebot.TeleBot(config.TOKEN)

# chats = dict()
with open('chats', 'rb') as f:
    chats = pickle.load(f)

with open('new_year_wishes', 'r', encoding='utf-8') as f:
    wishes = f.read().split('\n')

admins = [1015121341]
lev_id = 943593424
my_chat_id = 1015121341
last_mes = [1015121341]


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        return message.from_user.id in admins


class IsRegistered(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_reg'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            return message.from_user.id in chats[message.chat.id]['users']
        except:
            return False


class IsChatRegistered(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_chat_reg'

    @staticmethod
    def check(message: telebot.types.Message):
        return message.chat.id in chats


class IsChatActive(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_chat_active'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            return chats[message.chat.id]['active']
        except:
            return False


class IsActive(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_active'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            return chats[message.chat.id]['users'][message.from_user.id]['active']
        except:
            return False


class IncMessages(telebot.custom_filters.SimpleCustomFilter):
    key = 'inc_messages'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            last_mes[0] = message
            chats[message.chat.id]['users'][message.from_user.id]['messages_count'] += 1
        except:
            pass
        return False


# ---------------------------------------------ADMIN METHODS------------------------------------------------------------


@bot.message_handler(commands=['info'], is_admin=True)
def info(message):
    try:
        mes = []
        for chat_id, chat_info in chats.items():
            mes.append(f"Создан:{datetime.datetime.utcfromtimestamp(chat_info['creation_time']).strftime('%Y-%m-%d %H:%M:%S')} Участников:{len(chat_info['users'])}")
        bot.send_message(message.chat.id, '\n'.join(mes))
    except Exception as e:
        bot.send_message(message.chat.id, f'Что-то пошло не так {e}')
    bot.send_message(message.chat.id, f"Всего чатов: {len(chats)}")


@bot.message_handler(commands=['reg_chat'], is_admin=True)
def reg_chat(message):
    chat_id = message.chat.id
    password = ''.join(message.text.split()[1:])
    if password == config.main_password:
        if chat_id in chats:
            if chats[chat_id]['active']:
                bot.send_message(chat_id, 'Чат уже добавлен')
            else:
                chats[chat_id]['active'] = True
                bot.send_message(chat_id, 'Чат активирован')
            return
        chats[chat_id] = {'name': 'default',
                          'creation_time': time.time(),
                          'users': dict(),
                          'roulette_cd': 60*60,
                          'steal_cd': 60*60,
                          'enable_kills': False,
                          'active': True}
        bot.send_message(chat_id, 'Добавлен новый чат')
    else:
        bot.send_message(chat_id, 'Неверный пароль')


@bot.message_handler(commands=['unreg_chat'], is_admin=True)
def unreg_chat(message):
    chat_id = message.chat.id
    if chat_id not in chats:
        bot.send_message(message.chat.id, 'Чат ещё не добавлен')
        return
    chats[chat_id]['active'] = False
    bot.send_message(message.chat.id, 'Чат деактивирован')


@bot.message_handler(commands=['delete_chat'], is_admin=True)
def delete_chat(message):
    chat_id = message.chat.id
    if chat_id not in chats:
        bot.send_message(chat_id, 'Чат ещё не добавлен')
        return
    chats.pop(chat_id, 0)
    bot.send_message(chat_id, 'Чат удалён')


@bot.message_handler(commands=['notification'], is_admin=True)
def info(message):
    try:
        text = " ".join(message.text.split()[1:])
        for chat_id in chats:
            try:
                bot.send_message(chat_id, text)
            except Exception as e:
                print(e)
    except:
        pass


# -------------------------------------------USER METHODS---------------------------------------------------------------


@bot.message_handler(commands=['reg'], is_chat_active=True, is_active=False)
def reg(message):
    if message.from_user.id in chats[message.chat.id]['users']:
        chats[message.chat.id]['users'][message.from_user.id]['active'] = True
        bot.send_message(message.chat.id, message.from_user.first_name + ' вернулся(лась)')
        return
    new_user = {'first_name': message.from_user.first_name,
                'username': message.from_user.username,
                'coins': 100,
                'status': 'cutie',
                'unreg_last_time': time.time() - 60*60*48,
                'suicide_count': 0,
                'roulette_loses': 0,
                'roulette_last_time': time.time() - 60*60*24,
                'steal_last_time': time.time() - 60*60*24,
                'steal_count': 0,
                'steal_total': 0,
                'steal_fine': 0,
                'bet_count': 0,
                'bet_bet_total': 0,
                'bet_win_total': 0,
                'gift_count': 0,
                'gift_in': 0,
                'gift_out': 0,
                'wish_year': 0,
                'cur_wish': None,
                'messages_count': 0,
                'active': True}
    try:
        if len(new_user['username']) > 1:
            pass
    except Exception:
        bot.send_message(message.chat.id, 'У вас не установлен <username>')
        new_user['username'] = new_user['first_name']
    chats[message.chat.id]['users'][message.from_user.id] = new_user
    bot.send_message(message.chat.id, message.from_user.first_name + ' зарегистрирован(а)')


@bot.message_handler(commands=['reg_lev'], is_chat_active=True)
def reg_lev(message):
    new_user = {'first_name': 'Kviksteron',
                'username': 'FilthyFluffy',
                'coins': 100,
                'status': 'cutie',
                'unreg_last_time': time.time() - 60 * 60 * 48,
                'suicide_count': 0,
                'roulette_loses': 0,
                'roulette_last_time': time.time() - 60*60*24,
                'steal_last_time': time.time() - 60*60*24,
                'steal_count': 0,
                'steal_total': 0,
                'steal_fine': 0,
                'bet_count': 0,
                'bet_bet_total': 0,
                'bet_win_total': 0,
                'gift_count': 0,
                'gift_in': 0,
                'gift_out': 0,
                'wish_year': 0,
                'cur_wish': None,
                'messages_count': 0,
                'active': True}
    chats[message.chat.id]['users'][lev_id] = new_user
    bot.send_message(message.chat.id, 'Kviksteron зарегистрирован(а)')


@bot.message_handler(commands=['unreg'], is_chat_active=True, is_active=True)
def unreg(message):
    user = chats[message.chat.id]['users'][message.from_user.id]
    if (time.time() - user['unreg_last_time']) < 60*60*48:
        bot.send_message(message.chat.id, message.from_user.first_name + ', пожно покидать игру не чаще чем раз в два дня')
        return
    user['unreg_last_time'] = time.time()
    chats[message.chat.id]['users'][message.from_user.id]['active'] = False
    bot.send_message(message.chat.id, message.from_user.first_name + ' больше не участвует в этом беспределе')


@bot.message_handler(commands=['delete'], is_admin=True, is_chat_reg=True, is_reg=True)
def delete(message):
    chats[message.chat.id]['users'].pop(message.from_user.id, 0)
    bot.send_message(message.chat.id, message.from_user.first_name + ' удалён(а)')


@bot.message_handler(commands=['help'], is_chat_active=True, is_reg=True)
def display_commands(message):
    # bot.send_message(message.chat.id, chats[message.chat.id]['users'][message.from_user.id]['username'])
    mes = ['/reg - участвовать',
           '/unreg - перестать участвовать',
           '/очередь <описание> - создать очередь из 241 группы',
           '/queue <описание> - создать очередь из участников',
           '/show_users - показать участников',
           '/stat - статистика участника',
           '/вопрос <вопрос> - задать вопрос',
           '/suicide - умереть',
           '/😳 - не нажимать',
           '/roulette - сыграть в рулетку',
           '/wish - новогоднее пожелание для тебя',
           '/steal <@username> <amount> - украсть 💰',
           '/gift <@username> <amount> - подарить 🎁',
           '🏀⚽🎲🎯🎳🎰 - сделать ставку',
           '/cringe - запостить кринж',
           '/justice - # в разработке',
           '/duel - # в разработке']
    bot.send_message(message.chat.id, '\n'.join(mes))


@bot.message_handler(is_chat_active=True, is_reg=True, inc_messages=True)
def message_counter(message):
    pass


@bot.message_handler(commands=['stat'], is_chat_active=True, is_reg=True)
def stat(message):
    user = chats[message.chat.id]['users'][message.from_user.id]
    mes = [f"{user['first_name']}",
           f"Баланс: {user['coins']}💰",
           f"{user['suicide_count']}☠|{user['roulette_loses']}🔫|{user['steal_count']}🚷|{user['bet_count']}🎰|{user['gift_count']}🎁|{user['messages_count']}✉",
           f"Украдено: {user['steal_total']}💰",
           f"Штрафы: {user['steal_fine']}💰",
           f"Поставлено: {user['bet_bet_total']}💰",
           f"Выиграно: {user['bet_win_total']}💰",
           f"Подарено: {user['gift_out']}🎁",
           f"Получено: {user['gift_in']}🎁"]
    bot.send_message(message.chat.id, '\n'.join(mes))


@bot.message_handler(commands=['save_all_data'], is_admin=True)
def save_all_data(message):
    with open('chats', 'wb') as file:
        pickle.dump(chats, file)
        size = sys.getsizeof(file)
    if message is None:
        return
    if size > 100_000_000:
        bot.send_message(message.chat.id, 'Размер данных превысил 100Mb, сворачиваемся')
        raise SystemExit
    bot.send_message(message.chat.id, f'Данные сохранены, всего {size // 1024}Кб')


@bot.message_handler(commands=['update_users'], is_admin=True)
def update_users(message):
    users = chats[message.chat.id]['users']
    for user_id in users:
        tmp_user = users[user_id].copy()
        users[user_id] = {'coins': 100,
                          'status': 'cutie',
                          'unreg_last_time': time.time() - 60 * 60 * 48,
                          'suicide_count': 0,
                          'roulette_loses': 0,
                          'steal_count': 0,
                          'steal_total': 0,
                          'steal_fine': 0,
                          'bet_count': 0,
                          'bet_bet_total': 0,
                          'bet_win_total': 0,
                          'gift_count': 0,
                          'gift_in': 0,
                          'gift_out': 0,
                          'wish_year': 0,
                          'cur_wish': None,
                          'messages_count': 0,
                          'active': True}

        users[user_id].update(tmp_user)
    bot.send_message(message.chat.id, 'Пользовательские данные обновлены')


@bot.message_handler(commands=['update_all_users'], is_admin=True)
def update_all_users(message):
    for chat_id in chats:
        try:
            users = chats[chat_id]['users']
            for user_id in users:
                tmp_user = users[user_id].copy()
                users[user_id] = {'coins': 100,
                                  'status': 'cutie',
                                  'unreg_last_time': time.time() - 60 * 60 * 48,
                                  'suicide_count': 0,
                                  'roulette_loses': 0,
                                  'steal_count': 0,
                                  'steal_total': 0,
                                  'steal_fine': 0,
                                  'bet_count': 0,
                                  'bet_bet_total': 0,
                                  'bet_win_total': 0,
                                  'gift_count': 0,
                                  'gift_in': 0,
                                  'gift_out': 0,
                                  'wish_year': 0,
                                  'cur_wish': None,
                                  'messages_count': 0,
                                  'active': True}
                users[user_id].update(tmp_user)
        except Exception as ex:
            bot.send_message(message.chat.id, str(ex))

    bot.send_message(message.chat.id, 'Пользовательские данные обновлены')


@bot.message_handler(commands=['show_users'], is_chat_active=True, is_reg=True)
def show_users(message):
    try:
        users = chats[message.chat.id]['users']
        mes = [('✅' + value['first_name'] if value['active'] else '❌' + value['first_name'], value['coins'], value['messages_count']) for key, value in users.items()]
        mes.sort(key=lambda x: x[1], reverse=True)
        mes = [f"{x[0]}: {x[1]}💰 | {x[2]}✉" for x in mes]
        bot.send_message(message.chat.id, 'Список участников:\n' + '\n'.join(mes))
    except Exception as e:
        bot.send_message(message.chat.id, f'Error {e}')


@bot.message_handler(commands=['очередь'], is_chat_active=True, is_reg=True)
def queue_241(message):
    lower_text = message.text.lower()
    kitties = config.nyashki
    mul = 1
    if lower_text.find('англ') != -1:
        mul = 2
        if lower_text.find('1') != -1:
            group = 1
        elif lower_text.find('2') != -1:
            group = 2
        else:
            bot.send_message(message.chat.id, 'Группа (1 или 2) не указана')
            return
        kitties = []
        for i in config.nyashki:
            if i[1] == group:
                kitties.append(i)
    random.shuffle(kitties)
    emo = config.emoji
    for i in emo:
        random.shuffle(i)
    mes = [message.text[1:].upper() + '\n']
    for i in range(len(kitties)):
        mes.append(str(i + 1) + ') ' + kitties[i][0] + ' ' + emo[i * mul // 3][i * mul % 3])
    bot.send_message(message.chat.id, '\n'.join(mes))


@bot.message_handler(commands=['queue'], is_chat_active=True, is_reg=True)
def queue(message):
    try:
        chat_id = message.chat.id
        users = list(chats[chat_id]['users'].values())
        num = len(users)
        random.shuffle(users)
        mes = [f"{i+1}){user['first_name']} {random.choice(config.emoji[round(i*5//num)])}" for i, user in enumerate(users)]
        bot.send_message(chat_id, ' '.join(message.text.split()[1:]) + '\n' + '\n'.join(mes))
    except Exception as ex:
        bot.send_message(message.chat.id, f"Что-то пошло не так: {ex}")


@bot.message_handler(commands=['😳'], is_chat_active=True, is_active=True)
def gay_game(message):
    game = random.choice(config.games)
    if game != '':
        with open("wolf.png", "rb") as file:
            data = file.read()
        mes = bot.send_photo(message.chat.id, photo=data)
        time.sleep(10)
        bot.delete_message(message.chat.id, mes.message_id)


@bot.message_handler(commands=['suicide'], is_chat_active=True, is_active=True)
def suicide(message):
    if message.from_user.id in chats[message.chat.id]['users']:
        user = chats[message.chat.id]['users'][message.from_user.id]
        try:
            bot.ban_chat_member(message.chat.id, message.from_user.id)
        except:
            pass
        bot.send_message(message.chat.id, user['first_name'] + random.choice(config.death_phrases))
        user['suicide_count'] += 1
        if user['suicide_count'] % 5 == 0:
            bot.send_message(message.chat.id, user['first_name'] + ' не хотел жить уже ' + str(user['suicide_count']) + ' раз(а)')
        bot.unban_chat_member(message.chat.id, message.from_user.id)
    else:
        bot.send_message(message.chat.id, message.from_user.first_name + ' не зарегистрирован(а)')


@bot.message_handler(commands=['вопрос'], is_chat_active=True, is_active=True)
def answer(message):
    question = '+'.join(message.text.split()[1:]).strip("!@#<>&?")
    if question is None:
        return
    elif len(question) == 0:
        return

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:76.0) Gecko/20100101 Firefox/76.0)'}
    end_str = '&lr=213&clid=2261451&win=471&src=suggest_B'
    r = requests.get('https://yandex.ru/search/?lr=213&clid=2261449&win=471&text=' + question + end_str, headers=headers)
    html = BS(r.content, 'html.parser')
    res = html.select(".fact-answer")
    if not res:
        bot.send_message(message.chat.id, 'Не могу ответить, яндекс узнал что я робот')
        return
    try:
        if res is not None:
            for line in res:
                answer.append(line.text)
        else:
            bot.send_message(message.chat.id, 'Не знаю', reply_to_message_id=message.message_id)
            return
    except AttributeError:
        bot.send_message(message.chat.id, 'Не могу ответить, AttributeError')
        return
    except BaseException:
        bot.send_message(message.chat.id, 'Не могу ответить, неизвестная ошибка')
        return
    else:
        bot.send_message(message.chat.id, '\n'.join(answer), reply_to_message_id=message.message_id)


@bot.message_handler(commands=['set_roulette_cd'], is_chat_reg=True, is_admin=True)
def set_roulette_cd(message):
    try:
        cd = int(message.text.split()[1])
        if cd < 5 or cd > 24*60:
            bot.send_message(message.chat.id, 'Неверно указано время')
        else:
            chats[message.chat.id]['roulette_cd'] = cd*60
            bot.send_message(message.chat.id, 'Установлена задержка ' + str(cd) + 'мин')
    except:
        pass


@bot.message_handler(commands=['enable_kills'], is_chat_reg=True, is_admin=True)
def enable_kills(message):
    if chats[message.chat.id]['enable_kills']:
        bot.send_message(message.chat.id, 'Убийства отключены')
        chats[message.chat.id]['enable_kills'] = False
    else:
        bot.send_message(message.chat.id, 'Убийства включены')
        chats[message.chat.id]['enable_kills'] = True


@bot.message_handler(commands=['roulette'], is_chat_active=True, is_active=True)
def roulette(message):
    chat = chats[message.chat.id]
    last_time = chats[message.chat.id]['users'][message.from_user.id]['roulette_last_time']
    dif = time.time() - last_time
    cd = chat['roulette_cd']
    if dif < cd:
        if cd - dif < 60:
            bot.send_message(message.chat.id, 'Слишком рано, следующая попытка через ' + str(round(cd - dif)) + 'сек')
        else:
            bot.send_message(message.chat.id, 'Слишком рано, следующая попытка через ' + str(round((cd - dif) / 60)) + 'мин')
        return
    chats[message.chat.id]['users'][message.from_user.id]['roulette_last_time'] = time.time()
    bot.send_message(message.chat.id, 'Игра в русскую рулетку 🤡, кому-то придётся умереть')
    mes_id = bot.send_message(message.chat.id, '5').message_id
    time.sleep(1)
    for i in range(4):
        bot.edit_message_text(text=f'{4 - i}', chat_id=message.chat.id, message_id=mes_id)
        time.sleep(1)
    bot.edit_message_text(text='💥', chat_id=message.chat.id, message_id=mes_id)
    users = chat['users']
    dead_id = random.choice([key for key, value in users.items() if value['active']])
    user = chat['users'][dead_id]
    if chat['enable_kills']:
        try:
            bot.ban_chat_member(message.chat.id, dead_id)
        except:
            pass
    bot.send_message(message.chat.id, user['first_name'] + ' мертв(а) ☠')
    user['roulette_loses'] += 1
    bot.unban_chat_member(message.chat.id, dead_id)


@bot.message_handler(content_types=['dice'], is_chat_active=True, is_active=True)
def bet(message):
    emoji = message.dice.emoji
    user = chats[message.chat.id]['users'][message.from_user.id]
    if message.forward_from is not None:
        bot.send_message(message.chat.id, 'Партия разочаровалась в вас, -15 кредитов', reply_to_message_id=message.message_id)
        user['coins'] = 0 if user['coins'] <= 15 else user['coins'] - 15
        return
    if emoji in ['🏀', '⚽']:
        if user['coins'] < 4:
            bot.send_message(message.chat.id, 'Нет монет', reply_to_message_id=message.message_id)
            return
        prize = (message.dice.value - 1) * 2
        user['coins'] += prize - 4
        bot.send_message(message.chat.id, 'Ставка: 4 Выигрыш: ' + str(prize) + ' Баланс: ' + str(user['coins']), reply_to_message_id=message.message_id)
        user['bet_count'] += 1
        user['bet_bet_total'] += 4
        user['bet_win_total'] += prize
    elif emoji in ['🎲', '🎯', '🎳']:
        if user['coins'] < 5:
            bot.send_message(message.chat.id, 'Нет монет', reply_to_message_id=message.message_id)
            return
        prize = (message.dice.value - 1) * 2
        user['coins'] += prize - 5
        bot.send_message(message.chat.id, 'Ставка: 5 Выигрыш: ' + str(prize) + ' Баланс: ' + str(user['coins']),
                         reply_to_message_id=message.message_id)
        user['bet_count'] += 1
        user['bet_bet_total'] += 5
        user['bet_win_total'] += prize
    elif emoji == '🎰':
        if user['coins'] < 4:
            bot.send_message(message.chat.id, 'Нет монет', reply_to_message_id=message.message_id)
            return
        if message.dice.value in [1, 22, 43, 64]:
            user['coins'] += 60
            bot.send_message(message.chat.id, 'Ставка: 4 Выигрыш: 64 Баланс: ' + str(user['coins']),
                             reply_to_message_id=message.message_id)
            user['bet_win_total'] += 64
        else:
            user['coins'] -= 4
            bot.send_message(message.chat.id, 'Ставка: 4 Выигрыш: 0 Баланс: ' + str(user['coins']),
                             reply_to_message_id=message.message_id)
        user['bet_count'] += 1
        user['bet_bet_total'] += 4


@bot.message_handler(commands=['set_steal_cd'], is_chat_reg=True, is_admin=True)
def set_steal_cd(message):
    try:
        cd = int(message.text.split()[1])
        if cd < 0 or cd > 24*60:
            bot.send_message(message.chat.id, 'Неверно указано время')
        else:
            chats[message.chat.id]['steal_cd'] = cd*60
            bot.send_message(message.chat.id, 'Установлена задержка ' + str(cd) + 'мин')
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так...')


@bot.message_handler(commands=['steal'], is_chat_active=True, is_active=True)
def steal(message):
    chat_id = message.chat.id
    try:
        users = {user_id: user for user_id, user in chats[chat_id]['users'].items() if user['active']}
        thief_id = message.from_user.id
        data = message.text.split()
        if len(data) < 2:
            return
        victim_username = data[1].removeprefix('@')
        try:
            steal_amount = int(data[2])
            if steal_amount <= 0 or steal_amount > 50:
                bot.send_message(chat_id, 'Сумма кражи должна быть от 1 до 50')
                return
        except:
            bot.send_message(chat_id, 'Неверно указана сумма кражи')
            return
        if users[thief_id]['username'] == victim_username:
            bot.send_message(chat_id, 'Нельзя красть у себя')
            return
        victim_id = ''
        for user_id, user in users.items():
            if user['username'] == victim_username:
                victim_id = user_id
                break
        if victim_id == '':
            bot.send_message(chat_id, f'{victim_username} не участвует')
            return
        cd = chats[chat_id]['steal_cd']
        dif = time.time() - users[thief_id]['steal_last_time']
        if dif < cd:
            if cd - dif < 60:
                bot.send_message(chat_id, 'Слишком рано, следующая попытка через ' + str(round(cd - dif)) + 'сек')
            else:
                bot.send_message(chat_id, 'Слишком рано, следующая попытка через ' + str(round((cd - dif) / 60)) + 'мин')
            return
        users[thief_id]['steal_last_time'] = time.time()
        if random.random() < 0.65:
            if users[victim_id]['coins'] < steal_amount:
                steal_amount = users[victim_id]['coins']
                users[victim_id]['coins'] = 0
                users[thief_id]['coins'] += steal_amount
                bot.send_message(chat_id, users[thief_id]['first_name'] + ' украл(а) у ' + users[victim_id]['first_name'] + f' все деньги ({steal_amount}💰)')
            else:
                users[victim_id]['coins'] -= steal_amount
                users[thief_id]['coins'] += steal_amount
                bot.send_message(chat_id, users[thief_id]['first_name'] + ' украл(а) у ' + users[victim_id]['first_name'] + f' {steal_amount}💰')
            users[thief_id]['steal_count'] += 1
            users[thief_id]['steal_total'] += steal_amount
        else:
            if users[thief_id]['coins'] < steal_amount:
                steal_amount = users[thief_id]['coins']
            users[thief_id]['coins'] -= steal_amount
            users[thief_id]['steal_fine'] += steal_amount
            ids = list(users.keys())
            ids.remove(thief_id)
            random.shuffle(ids)
            num_users = len(ids)
            remain = steal_amount % num_users
            one = 1
            for i in ids:
                if remain <= 0:
                    one = 0
                chats[chat_id]['users'][i]['coins'] += steal_amount // num_users + one
                remain -= 1
            bot.send_message(chat_id, f"{users[thief_id]['first_name']} был(а) пойман(а) во время кражи и заплатил(а) штраф {steal_amount}💰 (распределено между всеми участниками)")
    except Exception as e:
        bot.send_message(chat_id, f'Что-то пошло не так... {e}')


@bot.message_handler(commands=['_song'], is_chat_active=True, is_active=True)
def song(message):
    for line in config.song:
        bot.send_message(message.chat.id, line)
        time.sleep(0.42)


@bot.message_handler(commands=['gift'], is_chat_active=True, is_active=True)
def gift(message):
    chat_id = message.chat.id
    try:
        users = {user_id: user for user_id, user in chats[chat_id]['users'].items() if user['active']}
        source_id = message.from_user.id
        data = message.text.split()
        destination_username = data[1].removeprefix('@')
        try:
            gift_amount = int(data[2])
            if gift_amount <= 0:
                bot.send_message(chat_id, 'Сумма должна быть больше 0')
                return
        except:
            bot.send_message(chat_id, 'Неверно указана сумма')
            return
        if users[source_id]['username'] == destination_username:
            bot.send_message(chat_id, 'Нельзя дарить себе')
            return
        destination_id = ''
        for user_id, user in users.items():
            if user['username'] == destination_username:
                destination_id = user_id
                break
        if destination_id == '':
            bot.send_message(chat_id, f'{destination_username} не участвует')
            return
        if users[source_id]['coins'] < gift_amount:
            bot.send_message(chat_id, 'Нет монет')
            return
        users[source_id]['coins'] -= gift_amount
        users[source_id]['gift_out'] += gift_amount
        users[source_id]['gift_count'] += 1
        users[destination_id]['coins'] += gift_amount
        users[destination_id]['gift_in'] += gift_amount
        bot.send_message(chat_id, f"{users[source_id]['first_name']} подарил(а) {users[destination_id]['first_name']} {gift_amount}🎁")
    except Exception as e:
        bot.send_message(chat_id, f'Что-то пошло не так... {e}')


@bot.message_handler(commands=['kill'], is_admin=True, is_reg=True)
def kill(message):
    print("Бот убит")
    bot.send_message(last_mes[0].chat.id, "Бот убит")
    save_all_data(None)
    bot.stop_polling()


@bot.message_handler(commands=['cringe'], is_chat_active=True, is_active=True)
def cringe(message):
    try:
        dir = 'C:/Users/RedBeam/PycharmProjects/Telagram_bot_test/cringes'
        file_name = random.choice([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
        file_name = 'cringes/' + file_name
        if file_name.endswith('mp4'):
            bot.send_video(message.chat.id, open(file_name, 'rb'))
        elif file_name.endswith('g'):
            bot.send_photo(message.chat.id, open(file_name, 'rb'))
        elif file_name.endswith('gif'):
            bot.send_document(message.chat.id, open(file_name, 'rb'))
        elif file_name.endswith('tgs'):
            bot.send_sticker(message.chat.id, open(file_name, 'rb'))
    except Exception as ex:
        bot.send_message(message.chat.id, f"Что-то пошло не так: {ex}")


@bot.message_handler(commands=['wish'], is_chat_active=True, is_active=True)
def wish(message):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    user = chats[message.chat.id]['users'][message.from_user.id]
    if month != 1 and month != 12 or month == 1 and day > 20 or month == 12 and day < 10:
        bot.send_message(message.chat.id, "Пожелания доступны только во время нового года")
        return
    if month == 12:
        year += 1
    if year == user['wish_year']:
        bot.send_message(message.chat.id, f"{user['first_name']}, ты уже получил(а) пожелание:\n{user['cur_wish']}")
        return
    user['wish_year'] = year
    user['cur_wish'] = random.choice(wishes)
    bot.send_message(message.chat.id, f"❄{user['first_name']}❄\n{user['cur_wish']}")


@bot.message_handler(commands=['justice'], is_chat_active=True, is_active=True)
def justice(message):
    bot.send_video(message.chat.id, open("i_can't.mp4", 'rb'))


@bot.message_handler(commands=['duel'], is_chat_active=True, is_active=True)
def duel(message):
    bot.send_video(message.chat.id, open("i_can't.mp4", 'rb'))


def guess_game(message):
    pass  # Доделать игру 'составь слово'


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsRegistered())
bot.add_custom_filter(IsChatRegistered())
bot.add_custom_filter(IsActive())
bot.add_custom_filter(IsChatActive())
bot.add_custom_filter(IncMessages())


while True:
    print(f"Бот запущен {datetime.datetime.now()}")
    bot.send_message(my_chat_id, f"Бот запущен {datetime.datetime.now()}")
    try:
        bot.infinity_polling(skip_pending=True)
    except BaseException as e:
        bot.stop_polling()
        print(f"Бот умер: Exception: {e}")
        save_all_data(None)
        bot.send_message(my_chat_id, f"Бот умер( перезапуск через 1сек {e}")
        time.sleep(1)


