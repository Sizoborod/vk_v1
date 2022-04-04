import bs4 as bs4
import requests
import vk_api, random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

HELLO = ['Добрый день!', 'Приветствую!', 'Доброго времени суток!', 'Здравствуйте!',
         'Посылаю тебе тысячу приветствий, о мой друг!', 'Не верю своим глазам! А ну-ка, протри-ка мне стекла!',
         'Мне кажется, или я реально тебя вижу!', 'Ну ничего себе какие люди нарисовались перед моими глазами!',
         'Мираж! Это точно мираж! Ну, не может быть, что я вижу тебя прямо перед собой!']

TOKEN = '7e067adbfea7dca4d562747ea10c5521701397d6c2c34fe79117b3a67bf7adec8f13b8d74f9db267e9c49'
vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)
longpoll_bot = VkBotLongPoll(vk, 152871790)

def send_messadges(chat_id, text):
    random_id = random.randint(0,10000000)
    vk.method('messages.send', {'chat_id': chat_id, 'message': text, 'random_id': random_id})

def write_msg(user_id, text):
    random_id = random.randint(0, 10000000)
    vk.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': random_id})


def _get_user_name_from_vk_id(user_id):
    request = requests.get("https://vk.com/id" + str(user_id))
    bs = bs4.BeautifulSoup(request.text, "html.parser")
    print(bs)


    user_name = str(bs.text.split(' ')[:1])

    return user_name.split()[0]


def gg():
    for event in longpoll.listen():
        print(event.type)
        print(vars(event))
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if event.from_chat:
                    msg = event.text
                    print(msg)
                    chat_id = event.chat_id
                    send_messadges(chat_id, msg)
                    write_msg(event.user_id, 'ку')

        '''if event.type == VkBotEventType.MESSAGE_NEW:'''
        '''    print('Новое сообщение:')'''
        '''    print('Для меня от:', event.obj.message['from_id'])'''
        '''    print('Текст:', event.obj.message['text'])'''
        '''    vk_get = vk.get_api()'''
        '''    vk_get.messages.send(user_id=event.obj.message['from_id'],'''
        '''                     message="Спасибо, что написали нам. Мы обязательно ответим",'''
        '''                     random_id=random.randint(0, 2 ** 64))'''
        '''if event.type == VkBotEventType.MESSAGE_TYPING_STATE:'''
        '''    print(f'Печатает {event.obj.from_id} для {event.obj.to_id}')'''
        '''if event.type == VkBotEventType.GROUP_JOIN:'''
        '''    print(f'{event.obj.user_id} вступил в группу!')'''


print(_get_user_name_from_vk_id(24468644))