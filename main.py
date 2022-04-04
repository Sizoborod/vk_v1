import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from Bot import VkBot, MSG_WELCOME
from config import TOKEN as TOKEN
from config import ADMIN_ID

vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)
users = []
teather = False


def send_messadges(chat_id, text):
    random_id = random.randint(0, 10000000)
    vk.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': random_id})


def write_msg(user_id, message):
    random_id = random.randint(0, 10000000)
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id})


def main():
    print("Server started")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                for i in range(len(users)):
                    if event.user_id == users[i]._USER_ID:
                        user_id = i
                        break
                else:
                    user_id = len(users)
                    users.append(VkBot(event.user_id))
                print('New message:')
                print(f'For me by: {event.user_id} ')
                message, teather = users[user_id].new_message(event.text)

                if teather:
                    print('Ответы отправлены учителю')
                    nn, tt = users[user_id].check_data[3], users[user_id].check_data[4][-2:]
                    f1 = f'Тест - {users[user_id].check_data[4][:-2]} прошел {users[user_id]._USERNAME}'
                    f2 = f' ID{event.user_id} на {nn}({int(tt)}) - '
                    print(nn,tt, type(nn), type(tt))
                    f3 = f'{round(int(nn)/int(tt) * 100)}%'
                    write_msg(ADMIN_ID, f1 + f2 + f3)
                    teather = False
                else:
                    users[user_id].send = False
                write_msg(event.user_id, message)

                if users[user_id].first:
                    users[user_id].first = False
                    write_msg(event.user_id, "".join(MSG_WELCOME))
                print('Text: ', event.text)


main()
