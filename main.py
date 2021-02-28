import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import sqlite3
import requests
con = sqlite3.connect('database.db')
cur = con.cursor()
try:
    cur.execute('''CREATE TABLE users(user_id UNIQUE, marriage TEXT, about TEXT, prize TEXT, who TEXT, nickname TEXT, duel TEXT, respect INT, duels_win INT, duels_lose INT)''')
    con.commit()
except:
    pass


# ------- bot token and connect api ----------
TOKEN = 'You token'
vk = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk, 202560573)
vks = vk.get_api()
# ---------------------------------------


def send(message='hello', keyboard=''):
    if event.from_chat:
        vk.method('messages.send', {'chat_id': event.chat_id, 'message': message, 'random_id': random.getrandbits(64), 'disable_mentions': 1, 'keyboard': keyboard})

def exec(execute):
    cur.execute(execute)
    con.commit()


def get(value, user_id):
    return cur.execute(f'''SELECT {value} FROM users WHERE user_id={user_id}''').fetchone()


def get_all(value):
    return cur.execute(f'''SELECT {", ".join(value)} FROM users''').fetchall()


# ------- longpool ---------
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:    # реакция на новые сообщения
        try:
            if event.obj['action']['type'] == 'chat_invite_user':
                send('Рады приветствовать вас в нашем чате😃👋')
            if event.obj['action']['type'] == 'chat_kick_user':
                send('Пользователь удалён из чата🕯😢')
        except:
            pass
        my_id = event.obj.from_id
        text = event.obj.text.lower()
        user_get = vks.users.get(user_ids=my_id, fields=['screen_name'])
        user_get = user_get[0]
        my_name, my_surname = user_get['first_name'], user_get['last_name']
        if 'reply_message' in event.obj:
            if '-' not in str(event.obj.reply_message['from_id']):
                user_id = event.obj.reply_message['from_id']
                sender_user_get = vks.users.get(user_ids=user_id , fields=['screen_name'])[0]
                user_name, user_surname = sender_user_get['first_name'], sender_user_get['last_name']
                sc2_name = sender_user_get['screen_name']
                cur.execute(
                    f'''INSERT OR IGNORE INTO users(user_id, marriage, about, prize, who, nickname, duel, duels_win, duels_lose) VALUES({user_id}, "no", "нет информации", "нет приза", "no", "no", "no", 0, 0)''')
                con.commit()
        else:
            user_name, user_surname = False, False

        try:
            status, whom, nickname = get('status', my_id)[0], get('who', my_id)[0], get('nickname', my_id)[0]
        except:
            cur.execute(
                f'''INSERT OR IGNORE INTO users(user_id, marriage, about, prize, who, nickname, duel) VALUES({my_id}, "no", "нет информации", "нет приза", "no", "no", "no")''')
            con.commit()

        if 'джек' in text[:5] or 'jack' in text[:5] or 'джо' in text[:4] or 'jo' in text[:3] or '/' in text[:2] or '!' in text[:2]:
            marriage = get('marriage', my_id)[0]
            if 'о мне' in text:
                exec(f'''UPDATE users SET about="{text.split("о мне")[1]}"''')
                send('Информация заполнена✅')
            elif 'как ты' in text:
                send('замурррчательно😸\nВпрочем как всегда)')
            elif 'браки' in text:
                marriages = []
                for i in get_all(['marriage']):
                    if i[0] != 'no':
                        marriages.append(i[0])
                marriages = '\n'.join(marriages)
                send(f'В данный момент в браке находятся:\n{marriages}')
            elif 'мой брак' in text:
                if marriage != 'no':
                    send(f'У вас есть брак с {marriage}')
                else:
                    send('У вас нет брака!')
            elif 'развод' in text:
                if marriage != 'no':
                    exec(f'''UPDATE users SET marriage="no" WHERE marriage="{my_name} {my_surname}"''')
                    exec(f'''UPDATE users SET marriage="no" WHERE marriage="{marriage}"''')
                    send(f'Теперь вы в разводе c {marriage}💔')
                else:
                    send('У вас и так нет браков❗')
            elif 'профиль' in text:
                res = cur.execute(
                    f'''SELECT marriage, about, prize, who, nickname, respect FROM users WHERE user_id={my_id}''').fetchall()[
                    0]
                marriage = 'нет брака' if res[0] == 'no' else res[0]
                about, prize = res[1], res[2]
                who = 'нет ктокалки' if res[3] == 'no' else res[3]
                nickname = 'нет ника' if res[4] == 'no' else res[4]
                respect = res[5] if res[5] != None else 0
                send(f'⭐⭐профиль⭐⭐\nВас зовут {my_name} {my_surname}\nБрак: {marriage}\nо вас: {about}\n'
                     f'приз: {prize}\n'
                     f'ктокалка: {who}\nник: {nickname}\n'
                     f'уважение: {respect}')

            elif 'кто я' in text:
                try:
                    wh = f"{random.choice(['копчённый', 'солённый', 'сладкий', 'жёсткий', 'мягкий', 'свежий', 'тухлый'])} " \
                         f"{random.choice(['нигер', 'человек', 'маг', 'инопланетянин', 'дитя мира', 'вареник', 'пельмень', 'оладушек'])}"
                    if get('who', my_id)[0] == 'no':
                        exec(f'''UPDATE users SET who="{wh}" WHERE user_id={my_id}''')
                        send(f'Вы {wh}')
                    else:
                        send(f"Вы {get('who', my_id)[0]}")
                except:
                    cur.execute(
                        f'''INSERT OR IGNORE INTO users(user_id, marriage, status, deads, who, nickname, respect) VALUES({my_id}, "no", "no", 0, "no", "no", 0)''')
                    con.commit()
            elif 'кто все' in text:
                member = vk.method('messages.getConversationMembers', {'peer_id': 2000000000 + event.chat_id})['items']
                members = []
                for i in member:
                    try:
                        nick = get('nickname', i['member_id'])[0]
                    except:
                        nick = 'нет ника!'
                    try:
                        gt = get('who', i['member_id'])[0]
                    except:
                        gt = 'нет ктокалки'
                    if nick == 'no':
                        nick = 'нет ника'
                    if gt == 'no':
                        gt = 'нет ктокалки'
                    if '-' not in str(i['member_id']):
                        user_get = vks.users.get(user_ids=i['member_id'], fields=['screen_name'])
                        user_get = user_get[0]
                        first_name = user_get['first_name']
                        last_name = user_get['last_name']

                        members.append(f'@{user_get["screen_name"]} ({first_name} {last_name} ({nick})) - {gt}')
                        print(f'@{user_get["screen_name"]} ({first_name} {last_name} ({nick})) - {gt}')
                st = '\n'.join(reversed(members))
                send(f"Участники беседы:\n {st}")
            elif 'кто' in text:
                send('Я уверен это...')
                member = vk.method('messages.getConversationMembers', {'peer_id': 2000000000 + event.chat_id})['items']
                rand = random.choice(member)
                while '-' in str(rand['member_id']):
                    rand = random.choice(member)
                result = vk.method('users.get', {'user_ids': rand['member_id'], 'fields': ['screen_name']})
                screen_name = result[0]['screen_name']
                send(f'@{screen_name} ({result[0]["first_name"]} {result[0]["last_name"]})')
            elif 'мой ник' in text:
                send(f'Вас зовут {nickname}')
            elif 'ник' in text:
                send(f'Ваш ник изменён на {text.split("ник")[1]}')
                exec(f'''UPDATE users SET nickname="{text.split('ник')[1]}" WHERE user_id={my_id}''')
            else:
                send('Введи команду😃')
        if 'кик' in text:
            send('хай-хет')
        if 'переименовать' in text:
            vk.method('messages.editChat', {'chat_id': event.chat_id, 'title': text.split('переименовать', maxsplit=1)[1]})
        try:
            if text == 'дуэль':
                if get("duel", my_id)[0] == 'no':
                    exec(f'UPDATE users SET duel="{user_id} 0" WHERE user_id={my_id}')
                    exec(f'UPDATE users SET duel="{my_id} 0" WHERE user_id={user_id}')
                    keyboard_1 = VkKeyboard(one_time=False, inline=True)
                    keyboard_1.add_callback_button(label='Да', color=VkKeyboardColor.POSITIVE)
                    keyboard_1.add_callback_button(label='Нет', color=VkKeyboardColor.NEGATIVE)
                    keyboard_1.add_line()
                    keyboard_1.add_callback_button(label='Отменить', color=VkKeyboardColor.SECONDARY)
                    send(f'{my_name} {my_surname} обьявил дуэль с {user_name} {user_surname}\n\n{user_name}, Вы принимаете дуэль?', keyboard_1.get_keyboard())
                else:
                    send('Сначала завершите текущий дуэль!')
            if 'отменить' in text:
                if get('duel', my_id)[0].split()[0] != 'no':
                    appon = int(get('duel', my_id)[0].split()[0])
                    exec(f'UPDATE users SET duel="no" WHERE user_id={appon}')
                    exec(f'UPDATE users SET duel="no" WHERE user_id={my_id}')
                    send('Дуэль отменён!')
                else:
                    send('У вас и так нет дуэлей!')
            keyboard_1 = VkKeyboard(one_time=False, inline=True)
            keyboard_1.add_callback_button(label='Выстрел🔫', color=VkKeyboardColor.SECONDARY)
            if get("duel", my_id)[0] != 'no':
                if 'да' in text:
                    duelant = get('duel', int(get('duel', my_id)[0].split()[0]))[0].split()[0]
                    if my_id == int(duelant):
                        send('Вы приняли дуэль!', keyboard_1.get_keyboard())
                        exec(f'UPDATE users SET duel="{get("duel", my_id)[0].split()[0]} 1" WHERE user_id={my_id}')
                        exec(f'UPDATE users SET duel="{my_id} 1" WHERE user_id={ int(get("duel", my_id)[0].split()[0])}')
                    else:
                        print(int(get('duel', my_id)[0].split()[0]))
                        send('Вам не обьявляли дуэль!')
                if 'нет' in text:
                    if my_id == int(get('duel', my_id)[0].split()[0]):
                        send('Вы отказались от дуэля☹\nТеперь ваше уважение равно нулю!')
                    else:
                        send('Вам не обьявляли дуэль!')
                    exec(f'UPDATE users SET duel="{my_id} 0" WHERE duel={my_id}')
                    exec(f'UPDATE users SET duel="{my_id} 0" WHERE user_id={my_id}')
                    exec(f'UPDATE users SET duel="no" WHERE user_id={my_id}')
            if 'выстрел' in text:
                if my_id == int(get('duel', int(get('duel', my_id)[0].split()[0]))[0].split()[0]):
                    user_get = vks.users.get(user_ids=int(get("duel", my_id)[0].split()[0]), fields=['screen_name'])
                    user_get = user_get[0]
                    aponent = f"@{user_get['screen_name']} ({user_get['first_name']} {user_get['last_name']})"
                    vybr = random.choice([f'Вы выстрелили и попали!\n{aponent} повержен!', 'Вы выстрелили и промахнулись!\nПришла очередь оппонента!'])
                    if 'попали' in vybr:
                        exec(f'UPDATE users SET duel="no" WHERE user_id={int(get("duel", my_id)[0].split()[0])}')
                        exec(f'UPDATE users SET duel="no" WHERE user_id={my_id}')
                        send(vybr)
                    else:
                        send(vybr, keyboard_1.get_keyboard())

            if text in ['старт', 'start', '/start', '/старт', 'привет', 'hello', '/hello', '/привет']:
                send('Наши команды: \nvk.com/@my_jack_bot-komandy-jack-bot')
            if 'рулетка' in text:
                send('Заряжаем револьер')
                rand = random.choice([' проиграли\nОсторожнее в следующий раз☹', ' выжили!\n поздравляю)'])
                send(f'{my_name}, вы нажали на курок и...{rand}')
            if user_name != False:
                if text == 'брак':
                    marriage = get('marriage', my_id)[0]
                    if my_id != user_id:
                        if marriage != 'no':
                            exec(f'''UPDATE users SET marriage="no" WHERE marriage="{my_name} {my_surname}"''')
                            exec(f'''UPDATE users SET marriage="no" WHERE marriage="{user_name} {user_surname}"''')
                        send(f'Брак с {user_name} {user_surname} установлен💍')
                        exec(f'''UPDATE users SET marriage="{user_name} {user_surname}" WHERE user_id={my_id}''')
                        exec(f'''UPDATE users SET marriage="{my_name} {my_surname}" WHERE user_id={user_id}''')
                    else:
                        send('Я вас понимаю, но как бы вы не хотели иметь брак с самим собой так нельзя☹')
                elif 'поздравляю' in text:
                    sender = text.split('поздравляю', maxsplit=1)[1]
                    if sender != '':
                        send(f'{user_name} {user_surname}, {my_name} {my_surname} поздравляет вас {sender}')
                    else:
                        send(f'{user_name} {user_surname}, {my_name} {my_surname} поздравляет вас!')
                if '+' in text or 'жиз' in text[:5]:
                    if my_id == user_id:
                        send('Вы не можете оказать уважение самому себе❗')
                    if respect != None:
                        send(f'Уважение оказано (+{text.count("+")})')
                        respect = get('respect', user_id)[0]
                        exec(f'UPDATE users SET respect={respect} + {text.count("+")} WHERE user_id={user_id}')
                    if respect == None:
                        exec(f'UPDATE users SET respect=0 WHERE user_id={user_id}')
                        exec(f'UPDATE users SET respect={respect} + {text.count("+")} WHERE user_id={user_id}')

                if 'приз' in text:
                    if '-' not in str(user_id):
                        if my_id == user_id:
                            send('Вы не можете дать приз самому себе❗')
                        else:
                            send(f'{user_name} {user_surname}, вам выдан приз {text.split("приз")[1]}')
                            exec(f'''UPDATE users SET prize="{text.split("приз", maxsplit=1)[1]}" WHERE user_id={user_id}''')
                    else:
                        send('Ошибка')

                # === roll-play commands ===
                if text == 'убить':
                    send(f'{my_name} {my_surname} убил(а) {user_name} {user_surname}')
                if text == 'спс' or text == 'спасибо':
                    send(f'{my_name} {my_surname} поблагодарил(а) {user_surname}')
                if text == 'минет':
                    send(f'{my_name} {my_surname} сделал(а) минет {user_surname}')
                if text == 'сжечь':
                    send(f'{my_name} {my_surname} сжёг {user_name} {user_surname}')
                if text == 'ахах':
                    send(f'{my_name} {my_surname} посмеялся над шуткой {user_name} {user_surname}')
                if text == 'секс':
                    send(f'{my_name} {my_surname} сделал секс с {user_name} {user_surname}')
                if text == 'кусь':
                    send(f'{my_name} {my_surname} укусил(а) {user_name} {user_surname}')
                if text == 'ебля':
                    send(f'{my_name} {my_surname} жёстко трахнул(а) {user_name} {user_surname}')
                if text == 'груповуха':
                    send(f'{my_name} {my_surname} и ещё 4 человека засунули свои концы в узкую дырку к {user_name} {user_surname}')
                if text == 'уебать':
                    send(f'{my_name} {my_surname} уебал {user_name} {user_surname}')
                if text == 'выкинуть в окно':
                    send(f'{my_name} {my_surname} выкинул в окно {user_name} {user_surname}')
                if text == 'сьесть':
                    send(f'{my_name} {my_surname} съел {user_name} {user_surname}')
                if text == 'уронить мать в канаву':
                    send(f'{my_name} {my_surname} уронил мать {user_name} {user_surname} в канаву')
                if text == 'опустить':
                    send(f'{my_name} {my_surname} опустил {user_name} {user_surname}')
                if text == 'порно':
                    send(f'бешеный карлик {my_name} {my_surname} жестко продолбил нежную белоснежку {user_name} {user_surname}')

            else:
                pass
        except:
            send('Ошибка!')