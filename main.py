import json
from collections import defaultdict
import datetime
import asyncio
import threading
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
from uuid import uuid4
from user_data import save_user, load_data, save_admin, write_data, load_posts_data, write_posts_data
from dotenv import load_dotenv
import os
load_dotenv("TOKEN.env")
token = os.getenv('BOT_TOKEN')
data = load_posts_data()
planned_queue = data["planned_queue"]
posts_queue = []
FIRST_STATE = 1
SECOND_STATE = 2
THIRD_STATE = 3
FOURTH_STATE = 4
FIFTH_STATE = 5
SIXTH_STATE = 6
SEVENTH_STATE = 7
EIGHTH_STATE = 8
NINES_STATE = 9
TENTH_STATE = 10
user_states = defaultdict(lambda: 0)
bot = Bot(token=token)
def get_statistic(bot, event):
    posts_data = load_posts_data()
    users_data = load_data()
    if users_data["users"][event.from_chat]["status"] == "admin":
        all_likes = posts_data["likes"]
        all_views = posts_data["views"]
        all_dislikes = posts_data["dislikes"]
        most_liked = 0
        most_disliked = 0
        most_viewed = 0
        max_likes = 0
        max_dislikes = 0
        max_views = 0
        for post in posts_data["sent_posts"]:
            likes = post["likes"]
            dislikes = post["dislikes"]
            views = post["views"]
            if likes > max_likes:
                max_likes = likes
                most_liked = post
            if dislikes > max_dislikes:
                max_dislikes = dislikes
                most_disliked = post
            if views > max_views:
                max_views = views
                most_viewed = post
        print(most_liked)
        print(most_disliked)
        print(most_viewed)
        bot.send_text(chat_id=event.from_chat, text=f"Просмотров за все время: {all_views}👁️\nЛайков за все время: {all_likes}👍\nДизлайков за все время: {all_dislikes}👎")
        bot.send_text(chat_id=event.from_chat, text=f"Пост с наибольшем кол-вом просмотров: {most_viewed["views"]}👁️")
        if most_liked["fileId"] == "":
            bot.send_text(chat_id=event.from_chat, text=most_viewed["caption"])
        else:
            print("hi")
            bot.send_file(chat_id=event.from_chat, file_id=most_viewed["fileId"], caption=most_liked["caption"] or None)
        bot.send_text(chat_id=event.from_chat, text=f"Пост с наибольшем кол-вом лайков: {most_liked["likes"]}👍")
        if most_liked["fileId"]=="":
            bot.send_text(chat_id=event.from_chat, text=most_liked["caption"])
        else:
            bot.send_file(chat_id=event.from_chat, file_id=most_liked["fileId"], caption=most_liked["caption"] or None)
        bot.send_text(chat_id=event.from_chat, text=f"Пост с наибольшем кол-вом дизлайков: {most_disliked["dislikes"]}👎")
        if most_disliked["fileId"] == "":
            bot.send_text(chat_id=event.from_chat, text=most_disliked["caption"])
        else:
            bot.send_file(chat_id=event.from_chat, file_id=most_disliked["fileId"], caption=most_disliked["caption"] or None)
    else:
        bot.send_text(chat_id=event.from_chat, text="К сожалению, у вас недостаточно прав на эту команду(")
scheduler_running = False
scheduler_lock = threading.Lock()
async def process_posts_queue(bot_instance):
    while True:
        try:

            data = load_posts_data()
            users_data = load_data()
            posts_queue = data.get("posts_queue", [])
            planned_queue = data.get("planned_queue", [])

            now = datetime.datetime.fromisoformat(str(datetime.datetime.now())[:-10])

            changed = False


            posts_to_remove_idx = []

            for idx, post in enumerate(posts_queue):
                if not post.get("sex") or not post.get("date") or not post.get("time"):
                    continue

                send_dt = datetime.datetime.fromisoformat(post["date"] + " " + post["time"])
                if send_dt <= now:
                    post_id = post.get("id")
                    fileId = post.get("fileId")
                    caption = post.get("caption") or ""
                    min_age = int(post.get("min_age", 0))
                    max_age = int(post.get("max_age", 0))
                    sex = post.get("sex")

                    for uid, user_info in users_data.get("users", {}).items():
                        try:
                            user_age = int(user_info.get("age", 0))
                            user_sex = user_info.get("sex", "")
                            if (min_age < user_age < max_age) and (user_sex == sex or sex == "both"):
                                if fileId:
                                    bot_instance.send_file(chat_id=uid, file_id=fileId, caption=caption or None, inline_keyboard_markup="{}".format(json.dumps([[

                                        {"text": "👍", "callbackData": f"view:{post_id}:0"},
                                        {"text": "👎", "callbackData": f"view:{post_id}:1"},
                          ]])))
                                elif caption:
                                    bot_instance.send_text(chat_id=uid, text=caption, inline_keyboard_markup="{}".format(json.dumps([[

                                        {"text": "👍", "callbackData": f"view:{post_id}:0"},
                                        {"text": "👎", "callbackData": f"view:{post_id}:1"},
                          ]])))
                        except Exception:
                            continue

                    posts_to_remove_idx.append(idx)

            for idx in reversed(posts_to_remove_idx):
                data["sent_posts"].append(posts_queue[idx])  # keep post for stats
                print(1,posts_queue)
                posts_queue.pop(idx)
                print(2,posts_queue)
                changed = True

            for idx, post in enumerate(planned_queue):
                if not post.get("sex") or not post.get("date") or not post.get("time") or not post.get("min_age") or not post.get("max_age"):
                    continue

                send_dt = datetime.datetime.fromisoformat(post["date"] + " " + post["time"])
                print(send_dt, now)
                if send_dt <= now:
                    fileId = post.get("fileId")
                    caption = post.get("caption") or ""
                    min_age = int(post.get("min_age", 0))
                    max_age = int(post.get("max_age", 0))
                    sex = post.get("sex")
                    for uid, user_info in users_data.get("users", {}).items():
                        try:
                            user_age = int(user_info.get("age", 0))
                            user_sex = user_info.get("sex", "")
                            if (min_age < user_age < max_age) and (user_sex == sex or sex == "both"):
                                if fileId:
                                    bot_instance.send_file(chat_id=uid, file_id=fileId, caption=caption or None)
                                else:
                                    if caption:
                                        bot_instance.send_text(chat_id=uid, text=caption)
                        except Exception:
                            continue

                    # reschedule to tomorrow (daily regular)
                    data["sent_posts"].append(post)
                    next_day = (send_dt.date() + datetime.timedelta(days=1)).isoformat()
                    new_post = {
                        "id": str(uuid4()),
                        "fileId": fileId,
                        "caption": caption,
                        "date": next_day,
                        "time": post["time"],
                        "min_age": min_age,
                        "max_age": max_age,
                        "sex": sex,
                        "planned": post["planned"],
                        "views": 0,
                        "viewers":[],
                        "likes":0,
                        "dislikes":0
                    }
                    planned_queue.append(new_post)
                    planned_queue.pop(idx)
                    changed = True

            if changed:
                data["posts_queue"] = posts_queue
                data["planned_queue"] = planned_queue
                write_posts_data(data)

            await asyncio.sleep(max(30, 60 - datetime.datetime.now().second))

        except Exception as e:
            print(f"Error in post scheduler: {e}")
            await asyncio.sleep(5)

def start_scheduler(bot_instance):
    """Start the async scheduler in a separate thread"""
    global scheduler_running

    with scheduler_lock:
        if scheduler_running:
            return
        scheduler_running = True

    def run_async_scheduler():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_posts_queue(bot_instance))

    scheduler_thread = threading.Thread(target=run_async_scheduler, daemon=True)
    scheduler_thread.start()


def edit_data(bot, event):
    bot.send_text(chat_id=event.from_chat, text = "Как вас зовут?",inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "Отмена", "callbackData": "call_back_id_cancel"}
                      ]])))
    user_states[event.from_chat] = FIFTH_STATE
def start(bot, event):
    try:
        data = load_data()
        if len(data['users']) == 0 or len(data['users'])== 1 and data["users"][event.from_chat]["registered"] == False:
            bot.send_text(chat_id=event.from_chat,
                          text=f"Привет👋\nМеня зовут Сэнди, давайте познакомимся? Как я могу к вам обращаться?")
            save_admin(event.from_chat)
            user_states[event.from_chat] = FIFTH_STATE

        else:
            if data['users'][event.from_chat]["status"] != 'admin':
                if data["users"][event.from_chat]["registered"] == False:
                    bot.send_text(chat_id=event.from_chat,
                                  text=f"Привет👋\nМеня зовут Сэнди, буду присылать вам прикольные штуки\nКак я могу к вам обращаться?")
                    save_user(event.from_chat)
                    user_states[event.from_chat] = FIFTH_STATE
                else:
                    bot.send_text(chat_id=event.from_chat,
                                  text=f"Привет👋\nМеня зовут Сэнди, буду присылать вам прикольные штуки")

            else:
                name = data['users'][event.from_chat]['name']
                bot.send_text(chat_id=event.from_chat,
                              text=f"Привет, {name}👋\nНа данный момент вы находитесь на должности администратора. Чтобы ознакомиться со списком команд введите /info")
    except:
        bot.send_text(chat_id=event.from_chat,
                      text=f"Привет👋\nМеня зовут Сэнди, буду присылать вам прикольные штуки про VK Teams\nКак я могу к вам обращатьcя?")
        save_user(event.from_chat)
        user_states[event.from_chat] = FIFTH_STATE



def ask_name(bot, event):
    name = event.text
    data = load_data()
    data["users"][event.from_chat]["name"] = name
    bot.send_text(chat_id=event.from_chat, text=f"Отлично☺️\nТеперь выберете ваш пол",
                  inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "Муж", "callbackData": "call_back_id_2", "style": "primary"},
                      {"text": "Жен", "callbackData": "call_back_id_3", "style": "attention"},
                      {"text": "Назад", "callbackData": "call_back_id_back"}
                  ]])))
    write_data(data)
    user_states[event.from_chat] = SIXTH_STATE


def ask_sex(bot, event, sex):
    try:
        data = load_data()
        data["users"][event.from_chat]["sex"] = sex
        write_data(data)
        user_states[event.from_chat] = SEVENTH_STATE
        bot.send_text(chat_id=event.from_chat, text="Еще чуть-чуть🤏\nОсталось только ввести ваш возраст",
                      inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "Назад", "callbackData": "call_back_id_back"}
                      ]])))
    except:
        bot.send_text(chat_id=event.from_chat, text="Некорректный ввод, попробуйте еще раз")


def ask_age(bot, event):
    try:
        data = load_data()
        age = int(event.text)

        data["users"][event.from_chat]["age"] = str(age)
        write_data(data)
        name = data["users"][event.from_chat]["name"]
        is_registered = data["users"][event.from_chat]["registered"]
        if data["users"][event.from_chat]["status"] == "user":
            if is_registered:
                bot.send_text(chat_id=event.from_chat,
                          text=f"Данные успешно изменены✅\nЕсли что-то не так, то нажмите на кнопку 'Изменить'")
            else:
                bot.send_text(chat_id=event.from_chat,
                              text=f"Приятно познакомиться, {name}. Жди полезных рассылок от меня😉\nЕсли что-то не так, то нажмите на кнопку 'Изменить'")
                data["users"][event.from_chat]["registered"] = True
            info(bot, event)
        else:
            if is_registered:
                bot.send_text(chat_id=event.from_chat,
                              text=f"Данные успешно изменены✅\nЕсли что-то не так, то нажмите на кнопку 'Изменить'")
                info(bot, event)

            else:
                bot.send_text(chat_id=event.from_chat,
                            text=f"Приятно познакомиться, {name}. Так как вы - мой первый пользователь, я автоматически сделал вас администратором. Чтобы ознакомиться со списком команд, введите /info")
                data["users"][event.from_chat]["registered"] = True

        user_states[event.from_chat] = 0
        write_data(data)
    except:
        bot.send_text(chat_id=event.from_chat, text="Некорректный ввод, введите число🔁")


def info(bot, event):
    data = load_data()
    try:
        user_id = data["users"][event.from_chat]
        name = user_id["name"]
        if user_id["sex"] == "male":
            sex = "Мужской👱"
        else:
            sex = "Женский👩"
        age = user_id["age"]
        if data['users'][event.from_chat]["status"] != 'admin':
            bot.send_text(chat_id=event.from_chat, text=f"Ваше имя : {name}\nВаш пол: {sex}\nВаш возраст: {age}",
                          inline_keyboard_markup="{}".format(json.dumps([[
                              {"text": "Изменить", "callbackData": "call_back_id_edit"}
                          ]])))
        else:
            bot.send_text(chat_id=event.from_chat,
                          text=f"Вот список, доступных вам, команд:\n"
                               f"/broadcast : Запустить рассылку\n"
                               f"/level_up : Назначить на должность администратора\n"
                               f"/level_down : Уволить с должности администратора\n"
                               f"/planned_broadcast : Добавить пост в очередь регулярных постов\n"
                               f"/remove_planned_post : Удалить пост из очереди регулярных постов\n"
                               f"/get_statistics : Удалить пост из очереди регулярных постов\n"
                               f"Ваши данные🪪\n"
                               f"Ваше имя : {name}\n"
                               f"Ваш пол: {sex}\n"
                               f"Ваш возраст: {age}\n"
                               f"Если что-то не так, нажмите на кнопку 'Изменить'", inline_keyboard_markup="{}".format(json.dumps([[
                              {"text": "Изменить", "callbackData": "call_back_id_edit"}
                          ]])))
    except:
        bot.send_text(chat_id=event.from_chat, text="Что-то пошло не так, попробуйте еще раз🔁")


def level_up(bot, event):
    try:
        data = load_data()
        if data['users'][event.from_chat]["status"] == "admin":
            bot.send_text(chat_id=event.from_chat,
                          text="Введите почту пользователя, чтобы назначить его на долность администратора")
            user_states[event.from_chat] = FIRST_STATE
        else:
            bot.send_text(chat_id=event.from_chat,
                          text="К сожалению, вы не можете использовать эту команду, так как вы не являетесь администратором😞")
    except:
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")


def level_up_continue(bot, event):
    try:
        data = load_data()
        user_id = event.text
        if data["users"][user_id]["status"] == "user":
            data["users"][user_id]["status"] = "admin"
            bot.send_text(chat_id=event.from_chat,
                          text=f'Пользователь {event.text} был повышен до должности "Администратор"🥳')
            bot.send_text(chat_id=user_id, text=f'Вас назначили на должность администратора🥳')
        else:
            bot.send_text(chat_id=event.from_chat,
                          text=f'Пользователь {event.text} уже назодится на должности "Администратор"')
        user_states[event.from_chat] = 0
    except:
        bot.send_text(chat_id=event.from_chat,
                      text="Произошла ошибка, скорее всего такого пользователя не существует. Попробуйте еще раз🔁")


def level_down(bot, event):
    try:
        data = load_data()
        if data['users'][event.from_chat]["status"] == "admin":
            bot.send_text(chat_id=event.from_chat,
                          text="Введите почту пользователя, чтобы снять его с должности администратора")
            user_states[event.from_chat] = SECOND_STATE
        else:
            bot.send_text(chat_id=event.from_chat,
                          text="К сожалению, вы не можете использовать эту команду, так как вы не являетесь администратором😞")
    except:
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")


def level_down_continue(bot, event):
    try:
        data = load_data()
        user_id = event.text
        if data["users"][user_id]["status"] == "admin":
            data["users"][user_id]["status"] = "user"
            bot.send_text(chat_id=event.from_chat,
                          text=f'Пользователь {event.text} был снят с должности "Администратор"📉')
            bot.send_text(chat_id=user_id, text=f'Вас сняли с должности администратора😞')
        else:
            bot.send_text(chat_id=event.from_chat,
                          text=f'Пользователь {event.text} итак не является администратором')
        user_states[event.from_chat] = 0
    except:
        bot.send_text(chat_id=event.from_chat,
                      text="Произошла ошибка, скорее всего такого пользователя не существует. Попробуйте еще раз🔁")


def broadcast(bot, event):
    try:
        data = load_data()
        posts_data = load_posts_data()
        posts_queue = posts_data["posts_queue"]
        if data['users'][event.from_chat]["status"] == "admin":
            bot.send_text(chat_id=event.from_chat,
                          text="Пришлите пост, который вы хотели бы разослать пользователям",inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "Отмена", "callbackData": "call_back_id_0", "style": "attention"}
                  ]])))
            new_post = {"id": str(uuid4()),
                        "fileId": False,
                        "caption": False,
                        "date": False,
                        "time": False,
                        "min_age": False,
                        "max_age": False,
                        "sex": False,
                        "planned": False,
                        "views": 0,
                        "viewers":[],
                        "likes": 0,
                        "dislikes": 0
                        }
            posts_queue.append(new_post)
            write_posts_data(posts_data)
            user_states[event.from_chat] = THIRD_STATE
        else:
            bot.send_text(chat_id=event.from_chat,
                          text="К сожалению, вы не можете использовать эту команду, так как вы не являетесь администратором😞")
    except:
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")
def planned_broadcast(bot, event):
    try:
        data = load_data()
        posts_data = load_posts_data()
        posts_queue = posts_data["posts_queue"]
        if data['users'][event.from_chat]["status"] == "admin":
            bot.send_text(chat_id=event.from_chat,
                          text="Пришлите пост, который вы хотели бы разослать пользователям",inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "Отмена", "callbackData": "call_back_id_0", "style": "attention"}
                  ]])))
            new_post = {"id": str(uuid4()),
                        "fileId": False,
                        "caption": False,
                        "date": False,
                        "time": False,
                        "min_age": False,
                        "max_age": False,
                        "sex": False,
                        "planned":True,
                        "views": 0,
                        "viewers":[],
                        "likes": 0,
                        "dislikes": 0
                        }
            posts_queue.append(new_post)
            write_posts_data(posts_data)
            user_states[event.from_chat] = THIRD_STATE
        else:
            bot.send_text(chat_id=event.from_chat,
                          text="К сожалению, вы не можете использовать эту команду, так как вы не являетесь администратором😞")
    except:
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")
def remove_planned_post(bot, event):
    global planned_queue
    for id, post in enumerate(planned_queue):
        fileId = post["fileId"]
        caption = post["caption"]
        bot.send_text(chat_id=event.from_chat, text=f"Пост номер {id}⬇️")
        if fileId and fileId != '':
            if caption:
                bot.send_file(chat_id=event.from_chat, file_id=fileId, caption=caption)
            else:
                bot.send_file(chat_id=event.from_chat, file_id=fileId)
        else:
            bot.send_text(chat_id=event.from_chat, text=caption)
    bot.send_text(chat_id=event.from_chat, text="Введите номер поста, рассылку которого хотите прекратить⬇️",inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "Отмена", "callbackData": "call_back_id_cancel", "style": "attention"}
                      ]])))
    user_states[event.from_chat] = TENTH_STATE
def remove(bot, event):
    data = load_posts_data()
    planned_queue = data["planned_queue"]
    idx = int(event.text)
    planned_queue.pop(idx)
    bot.send_text(chat_id=event.from_chat, text="Пост успешно удален из очереди✅")
    data["planned_queue"] = planned_queue
    write_posts_data(data)
def broadcast_time(bot, event):
    fileId = ''
    posts_data = load_posts_data()
    posts_queue = posts_data["posts_queue"]
    if event.text:
        caption = event.text
    elif event.data['parts'][0]['type'] != "forward":
        lena = len(event.data['parts'][0]['payload'])
        fileId = event.data['parts'][0]['payload']['fileId']
        if lena == 3:
            caption = event.data['parts'][0]['payload']['caption']
        else:
            caption = ''
    else:
        caption = event.data['parts'][0]['payload']['message']['text']
        fileId = event.data['parts'][0]['payload']['message']['parts'][0]['payload']['fileId']
        if caption[:29] == "https://files.myteam.mail.ru/":
            caption = False

    posts_queue[-1]["fileId"] = fileId
    posts_queue[-1]["caption"] = caption
    bot.send_text(chat_id=event.from_chat,
                  text="Отлично, если хотите разослать пост сейчас напишите 'now', иначе введите время отправки поста в формате dd.mm.yyyy hh:mm⬇️\nНапример: 19.09.2026 14:30",inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "Отмена", "callbackData": "call_back_id_0", "style": "attention"}
                  ]])))
    write_posts_data(posts_data)
    user_states[event.from_chat] = FOURTH_STATE


def sex_choose(bot, event):
    try:
        posts_data = load_posts_data()
        posts_queue = posts_data["posts_queue"]
        if event.text.lower() != 'now':
            date, time = event.text.split(" ")
            dater = date.split(".")
            date = dater[2] + "-" + dater[1] + "-" + dater[0]
        else:
            date, time = "now", "now"

        posts_queue[-1]["time"] = time
        posts_queue[-1]["date"] = date
        bot.send_text(chat_id=event.from_chat, text="С датой опредилились. Теперь давайте выберем пол получателей⬇️",
                      inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "Муж👱", "callbackData": "call_back_id_4", "style": "primary"},
                          {"text": "Жен👩", "callbackData": "call_back_id_5", "style": "attention"},
                          {"text": "Все👩👱", "callbackData": "call_back_id_6"},
                          {"text": "Отмена", "callbackData": "call_back_id_0", "style": "attention"}
                      ]])))
        user_states[event.from_chat] = EIGHTH_STATE
        write_posts_data(posts_data)
    except:
        bot.send_text(chat_id=event.from_chat, text="Введите корректную дату,️ либо 'Now'🔁")


def age_choose(bot, event):
    bot.send_text(chat_id=event.from_chat,
                  text="Есть! Теперь давайте выберем возраст получателей. Чтобы выбрать диапазон введите aa-aa⬇️\nНапример: 14-99",inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "Отмена", "callbackData": "call_back_id_0", "style": "attention"}
                  ]])))
    user_states[event.from_chat] = NINES_STATE


def isOK(bot, event):
    try:
        min_age, max_age = event.text.split("-")
        posts_data = load_posts_data()
        posts_queue = posts_data["posts_queue"]
        posts_queue[-1]["min_age"] = min_age
        posts_queue[-1]["max_age"] = max_age
        bot.send_text(chat_id=event.from_chat, text="Ваш пост выглядит так⬇️")
        fileId = posts_queue[-1]["fileId"]
        caption = posts_queue[-1]["caption"]
        if caption and fileId:
            bot.send_file(chat_id=event.from_chat, file_id=fileId, caption=caption)
        elif caption:
            bot.send_text(chat_id=event.from_chat, text=caption)
        elif fileId:
            bot.send_file(chat_id=event.from_chat, file_id=fileId)
        bot.send_text(chat_id=event.from_chat,
                      text="Вы точно хотите его отправить? В будущем удалить пост будет НЕЛЬЗЯ, только из очереди если он запланированный\n Выберете 'ДА' или 'НЕТ'",
                      inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "ДА", "callbackData": "call_back_id_1", "style": "primary"},
                          {"text": "НЕТ", "callbackData": "call_back_id_0", "style": "attention"}
                      ]])))
        write_posts_data(posts_data)
    except Exception as e:
        print(e)
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")


def go_back(bot, event, way):
    current_state = user_states[event.from_chat]
    if current_state == SIXTH_STATE:
        if way == "button":
            user_states[event.from_chat] = FIFTH_STATE
            edit_data(bot, event)
        else:
            ask_name(bot, event)
    elif current_state == SEVENTH_STATE:
        bot.send_text(chat_id=event.from_chat, text=f"Отлично☺️\nТеперь выберете ваш пол",
                      inline_keyboard_markup="{}".format(json.dumps([[
                          {"text": "Муж", "callbackData": "call_back_id_2", "style": "primary"},
                          {"text": "Жен", "callbackData": "call_back_id_3", "style": "attention"},
                          {"text": "Назад", "callbackData": "call_back_id_back"}
                      ]])))
        user_states[event.from_chat] = SIXTH_STATE
    elif current_state == FIFTH_STATE:
        broadcast(bot,event)
    else:
        user_states[event.from_chat] = max(0, current_state - 1)



def main(bot, event):
    if event.text == '/start':
        start(bot, event)
    elif event.text == "/level_up":
        level_up(bot, event)
    elif event.text == '/level_down':
        level_down(bot, event)
    elif event.text == '/broadcast':
        broadcast(bot, event)
    elif event.text == "/info":
        info(bot, event)
    elif event.text == "/planned_broadcast":
        planned_broadcast(bot,event)
    elif event.text == "/remove_planned_post":
        remove_planned_post(bot,event)
    elif event.text == "/get_statistics":
        get_statistic(bot, event)
    else:
        if user_states[event.from_chat] == FIRST_STATE:
            level_up_continue(bot, event)
        elif user_states[event.from_chat] == FIFTH_STATE:
            ask_name(bot, event)
        elif user_states[event.from_chat] == SIXTH_STATE:
            if event.text:
                bot.send_text(chat_id=event.from_chat, text="Некорректный ввод, попробуйте еще раз")
                go_back(bot, event, way = "text")
            else:
                ask_sex(bot, event, data["users"][event.from_chat]["sex"])
        elif user_states[event.from_chat] == SEVENTH_STATE:
            ask_age(bot, event)
        elif user_states[event.from_chat] == SECOND_STATE:
            level_down_continue(bot, event)
        elif user_states[event.from_chat] == THIRD_STATE:
            broadcast_time(bot, event)
        elif user_states[event.from_chat] == FOURTH_STATE:
            sex_choose(bot, event)
        elif user_states[event.from_chat] == EIGHTH_STATE:
            age_choose(bot, event)
        elif user_states[event.from_chat] == NINES_STATE:
            isOK(bot, event)
        elif user_states[event.from_chat]==TENTH_STATE:
            remove(bot,event)
        else:
            bot.send_text(chat_id=event.from_chat, text="Не удалось обработать ваш запрос")


def button_callback(bot, event):
    try:
        data = load_posts_data()
        posts_queue = data["posts_queue"]
        cb = event.data.get("callbackData")
        if cb and cb.startswith("view:"):

            cb1 = cb.split(":")
            print(cb1)
            post_id = cb1[1]
            user_id = event.from_chat


            post = None
            for p in data.get("sent_posts", []):
                print(p.get("id") ,post_id)
                if p.get("id") == post_id:
                    post = p
                    break

            if not post:
                bot.send_text(chat_id=user_id, text="Статистика для этого поста недоступна.")
                return

            viewers = post.setdefault("viewers", [])
            if user_id not in viewers:
                viewers.append(user_id)
                post["views"] += 1
                data["views"] += 1
                if cb1[2] == "0":
                    post["likes"] += 1
                    data["likes"] += 1
                else:
                    post["dislikes"] += 1
                    data["dislikes"] += 1
                write_posts_data(data)
                bot.send_text(chat_id=user_id, text="Спасибо за оценку!")
            else:
                bot.send_text(chat_id=user_id, text="Вы уже оценивали данный пост")
            return
        elif event.data['callbackData'] == "call_back_id_1":

            if posts_queue[-1]["date"] == "now":
                posts_queue[-1]["date"] = str(datetime.date.today())
                post_time = str(datetime.datetime.now()).split()
                post_time1 = post_time[1].split(":")
                posts_queue[-1]["time"] = post_time1[0] + ":" + post_time1[1]

            if posts_queue[-1]["planned"] == True:
                planned_queue.append(posts_queue[-1])
                posts_queue.pop(len(posts_queue)-1)
                data["planned_queue"] = planned_queue
            else:
                data["posts_queue"] = posts_queue
            write_posts_data(data)
            bot.send_text(chat_id=event.from_chat,
                          text="Пост успешно добавлен в очередь✅ Рассылка пройдет по заданному времени")
            user_states[event.from_chat] = 0
            start_scheduler(bot)

        elif event.data['callbackData'] == "call_back_id_0":
            posts_data = load_posts_data()
            posts_queue = posts_data["posts_queue"]
            posts_queue.pop(-1)
            print("bye", posts_queue)
            bot.send_text(chat_id=event.from_chat, text="Операция отменена❌")
            write_posts_data(posts_data)
            user_states[event.from_chat] = 0
        elif event.data['callbackData'] == "call_back_id_edit":
            data = load_data()
            data["users"][event.from_chat] = {}
            edit_data(bot, event)
        elif event.data['callbackData'] == "call_back_id_2":
            sex = "male"
            ask_sex(bot, event, sex)
        elif event.data['callbackData'] == "call_back_id_3":
            sex = "female"
            ask_sex(bot, event, sex)
        elif event.data['callbackData'] == "call_back_id_4":
            print(posts_queue)
            sex = "male"
            posts_data = load_posts_data()
            posts_queue = posts_data["posts_queue"]
            posts_queue[-1]["sex"] = sex
            write_posts_data(posts_data)
            age_choose(bot, event)
        elif event.data['callbackData'] == "call_back_id_5":
            sex = "female"
            posts_data = load_posts_data()
            posts_queue = posts_data["posts_queue"]
            posts_queue[-1]["sex"] = sex
            write_posts_data(posts_data)
            age_choose(bot, event)
        elif event.data['callbackData'] == "call_back_id_cancel":
            bot.send_text(chat_id=event.from_chat, text="Операция отменена❌")
            user_states[event.from_chat] = 0
        elif event.data['callbackData'] == "call_back_id_6":
            sex = "both"
            posts_data = load_posts_data()
            posts_queue = posts_data["posts_queue"]
            posts_queue[-1]["sex"] = sex
            write_posts_data(posts_data)
            age_choose(bot, event)
        elif event.data['callbackData'] == "call_back_id_back":
            print(user_states)
            go_back(bot, event, way = "button")

        else:
            bot.send_text(chat_id=event.from_chat, text="Некорректный ввод. Попробуйте еще раз🔁")
            return
    except Exception as e:
        bot.send_text(chat_id=event.from_chat, text="Произошла ошибка, попробуйте еще раз🔁")
        print(e)


bot.dispatcher.add_handler(MessageHandler(callback=main))
bot.dispatcher.add_handler(BotButtonCommandHandler(callback=button_callback))

bot.start_polling()
bot.idle()