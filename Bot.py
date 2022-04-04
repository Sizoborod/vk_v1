import random
import sqlite3

import bs4 as bs4
import requests

from test import TestSys

from config import ADMIN_ID

PRIVET = ['привет', 'здравств', 'hi', 'ку', 'ый день', 'ой ночи', 'ый вечер', 'ое утр']

HELLO = ['Добрый день!', 'Приветствую!', 'Доброго времени суток!', 'Здравствуйте!',
         'Посылаю тебе тысячу приветствий, о мой друг!', 'Не верю своим глазам! А ну-ка, протри-ка мне стекла!',
         'Мне кажется, или я реально тебя вижу!', 'Ну ничего себе какие люди нарисовались перед моими глазами!',
         'Мираж! Это точно мираж! Ну, не может быть, что я вижу тебя прямо перед собой!']

MSG_WELCOME = ["Я, vcBot для проведения тестирования по школьной физике.\n", "Тесты проводятся в чате. ",
               "Я задаю вопрос и жду от вас ответ в виде цифры от 1 до 5.\nМожно пропустить ответ на данный вопрос,",
               " с возможностью вернуться к нему в конце теста.\nРезультаты теста я отправлю вам и преподавателю.\n",
               "Познакомиться со списком команд можно используя команду - Помощь"]

MSG_HELP = ["Вот мои команды:\n", "Кто ты - vcBot раскажет о себе\n",
            "Список - vcBot выведет список доступных тестов\n",
            "Помощь - вывести команды vcBota\n", "Начать - начать тест\nТест 703 - Начнет тест под номером 703\n",
            "Пропустить - пропустить вопрос и перейти к следующему\n", "Надеюсь, все понятно"]


class VkBot:
    items = []

    def __init__(self, user_id):
        print(f"Создан объект бота! {user_id}")
        self._USER_ID = user_id
        self._USERNAME = self._get_user_name_from_vk_id(user_id)
        VkBot.items.append(self)
        self._COMMANDS = ["КТО ТЫ", "ТЕСТ", "ПОМОЩЬ", "ПОКА", "ПРОПУСТИТЬ", "ВВЕРХ", "ОТКРЫТЬ ТЕСТ",
                          "ЗАКРЫТЬ ТЕСТ", '12345', "СПИСОК ТЕСТОВ", "ОТКРЫТЬ ВСЕ ТЕСТЫ",
                          "ЗАКРЫТЬ ВСЕ ТЕСТЫ"]
        self.first = True
        self.test_users = []
        self.check_data = [0, 0, False, 0, '']
        self.send = False
        self.level = 0
        self.leaf_through_the_content = False

        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        sel = cur.execute(f"SELECT code, subject FROM tests").fetchall()
        self.con.close()
        self.list_of_topics_num = sorted(list(set([i[0] for i in sel])))
        print(self.list_of_topics_num)

    def _get_user_name_from_vk_id(self, user_id):
        '''получение страницы vc для парсинга и вынимания имени пользователя'''
        request = requests.get("https://vk.com/id" + str(user_id))
        bs = bs4.BeautifulSoup(request.text, "html.parser")
        user_name = self._clean_all_tag_from_str(bs.findAll("title")[0])
        return user_name.split()[0]

    # Метод для очистки от ненужных тэгов
    @staticmethod
    def _clean_all_tag_from_str(string_line):
        """
        Очистка строки stringLine от тэгов и их содержимых
        :param string_line: Очищаемая строка
        :return: очищенная строка
        """
        result = ""
        not_skip = True
        for i in list(string_line):
            if not_skip:
                if i == "<":
                    not_skip = False
                else:
                    result += i
            else:
                if i == ">":
                    not_skip = True
        return result

    def new_message(self, message):
        '''print('Сообщение', message)'''
        '''print('Варианты ответов', self.list_of_topics_num)'''
        '''print('Флаг продолжения', self.leaf_through_the_content)'''

        # Приветствеие
        if any(i in message.lower() for i in PRIVET):
            return f"{HELLO[random.randrange(len(HELLO))]} {self._USERNAME}!", False

        # Знакомство
        elif message.upper() == self._COMMANDS[0]:
            return "".join(MSG_WELCOME), False

        # открыть тест
        elif self._COMMANDS[6].lower() in message.lower() and self._USER_ID == ADMIN_ID:
            number_test = message.lower()[13:].strip()
            print('Открываю тест', number_test)
            text = self.open_test_db(number_test) + "\n" + self.list_test_db()
            return text, False

        # открыть все тесты
        elif self._COMMANDS[10].lower() == message.lower() and self._USER_ID == ADMIN_ID:
            print('Открываю все тесты')
            text = self.open_test_db() + "\n" + self.list_test_db()
            return text, False

        # закрыть тест
        elif self._COMMANDS[7].lower() in message.lower() and self._USER_ID == ADMIN_ID:
            number_test = message.lower()[12:].strip()
            print('Закрываю тест', number_test)
            text = self.close_test_db(number_test) + "\n" + self.list_test_db()
            return text, False

        # закрыть все тесты
        elif self._COMMANDS[11].lower() == message.lower() and self._USER_ID == ADMIN_ID:
            print('Закрываю все тесты')
            text = self.close_test_db() + "\n" + self.list_test_db()
            return text, False

        # запросить список тестов
        elif self._COMMANDS[9].lower() == message.lower():
            print('Запрашиваю список всех тестов')
            text = self.list_test_db()
            return text, False



        # Тест
        elif self._COMMANDS[1].lower() in message.lower():
            if message.lower() == self._COMMANDS[1].lower():
                msg, self.leaf_through_the_content = self.test_list(self.level)
                text = f"Перед вами список {['классов', 'глав', 'тестов'][self.level]}\n"
                return text + msg, False
            elif message.lower()[5:].strip().isdigit():
                print('нужный тест', message.lower()[5:].strip())
                self.test_number = message.lower()[5:].strip()
                if self.the_test_is_open(self.test_number):
                    for i in range(len(self.test_users)):
                        if self.test_number == self.test_users[i].n:
                            self.test_p_number = i
                            break
                    else:
                        self.test_p_number = len(self.test_users)
                        self.test_users.append(TestSys(self.test_number))
                    return self.test(self.test_users[self.test_p_number])
                else:
                    return f"Тест {self.test_number} закрыт для выполения", False
            else:
                return "".join(MSG_HELP), False

        # продолжение теста
        elif message.lower() == '#' or message.lower() == 'Далее'.lower():
            return self.test(self.test_users[self.test_p_number])

        # Пропустить вопрос
        elif message.upper() == self._COMMANDS[4] and self.check_data[2]:
            print('пропускают вопрос')
            return self.skip_question(self.test_users[self.test_p_number])

        # Движение в меню вниз
        elif message.lower() in self.list_of_topics_num and self.leaf_through_the_content and self.level < 2:
            print('Спуск вниз = ', self.level)
            self.level += 1
            text = f"Перед вами список {['классов', 'глав', 'тестов'][self.level]}\n"

            msg, self.leaf_through_the_content = self.test_list(self.level, message.lower())
            return text + msg, False

        # Движение по меню вверх
        elif message.lower() == self._COMMANDS[5].lower() and self.leaf_through_the_content and self.level > 0:
            print('Поднимаемся вверх = ', self.level)
            self.level -= 1
            text = f"Перед вами список {['классов', 'глав', 'тестов'][self.level]}\n"
            msg, self.leaf_through_the_content = self.test_list(self.level)
            return text + msg, False

        # ответы
        elif message.lower() in self._COMMANDS[8] and self.check_data[2]:
            return self.check(message.lower())

        # Помощь
        elif message.lower() == self._COMMANDS[2].lower():
            return "".join(MSG_HELP) + "\n" + "\n".join(self._COMMANDS), False

        # Пока
        elif message.lower() == self._COMMANDS[3].lower():
            return f"Пока-пока, {self._USERNAME}!", False



        else:
            return "Не понимаю о чем вы...\nВозможно вам поможет команда - Помощь", False

    def test(self, test_class):
        '''метод принимает экземпляр класса и формирует вопрос для передачи сообщения
        если вопросы закончились в тесте, то удаляет из списка тестов у экземпляра класса user
        формирует споровождающие тексты. Если вопросы закончились поднимает флаг отправки сообщения учителю
        о завершении теста с его результатами'''
        question, check_true, resu, name_t = test_class.testing()
        if question:
            a = '\n\n' + ''.join('' if question[i] is None else f"{i - 1}. {question[i]}\n" for i in range(2, 6)) + '\n'
            question = f"Тест - {self.test_users[self.test_p_number].name_test[:-2]}\nВопрос\n{question[0]}{a}", False
            self.check_data = [self.test_p_number, self.test_users[self.test_p_number].ans, check_true, resu, name_t]
        else:
            self.check_data = [0, 0, False, resu, name_t]
            self.test_users.pop(self.test_p_number)
            question = 'Вопросы закончились Ку-ку', True
        return question

    def check(self, user_ans):
        '''метод проверки ответов пользователя'''
        if str(user_ans) == str(self.check_data[1]):
            self.test_users[self.test_p_number].result += 1
            self.check_data = [0, 0, False, self.test_users[self.test_p_number].result,
                               self.test_users[self.test_p_number].name_test]
            next_ansver, flg = self.test(self.test_users[self.test_p_number])
            return f"Спасибо, ваш ответ принят.\n{next_ansver}", flg
        elif self.check_data[2]:
            next_ansver, flg = self.test(self.test_users[self.test_p_number])
            return f"Ваш ответ принят.\n{next_ansver}", flg
        else:
            return 'Вопросы закончились', True

    def skip_question(self, test_class):
        '''метод пропуска вопросов и формирования сообщения пользователю'''
        test_class.id_q.append(test_class.t_n)
        next_ansver, flg = self.test(self.test_users[self.test_p_number])
        return f"Вопрос отложен, будет доступен в конце.\n{next_ansver}", flg

    def test_list(self, n, t=False):
        '''метод формирует список(меню) тестов из которых можно потом вытрать соответствующий пункт'''
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        if n == 0:
            sel = cur.execute(f"SELECT class FROM tests").fetchall()
            self.list_of_topics = sorted(list(set([(i[0], 'класс') for i in sel])))
        elif n == 1 and t:
            sel = cur.execute(f"SELECT id_chapter, chapter FROM tests WHERE class={t}").fetchall()
            self.list_of_topics = sorted(list(set([i for i in sel])))
        elif n == 1 and not t:
            sel = cur.execute(f"SELECT id_chapter, chapter FROM tests").fetchall()
            self.list_of_topics = sorted(list(set([i for i in sel])))
        elif n == 2:
            sel = cur.execute(f"SELECT code, subject FROM tests WHERE id_chapter={t}").fetchall()
            self.list_of_topics = sorted(list(set([i for i in sel])))
        else:
            sel = ''
            self.list_of_topics = []

        self.con.close()
        self.list_of_topics_num = sorted(list(set([str(i[0]) for i in sel])))
        self.list_of_topics = [str(i[0]) + ' ' + str(i[1]) + '\n' for i in self.list_of_topics]
        print(self.list_of_topics_num)
        text_fut = "Поднятся в меню на уровень выше - вверх\n"
        if self.level == 2:
            text_cen = 'тест ' + ', тест '.join(str(i) for i in self.list_of_topics_num)
        else:
            text_cen = ' '.join(str(i) for i in self.list_of_topics_num)

        text_futer = f"Возможны варианты - {text_cen}\n" + text_fut
        if self.list_of_topics:
            return ''.join(self.list_of_topics) + 'Введите номер для продолжения\n' + text_futer, True
        else:
            return '\n\n\nОн пустой, возможно вы выбрали не тот пункт' + text_fut, True

    def open_test_db(self, number_test=False):
        '''метод открытия для выполнения теста путем изменения флага одного или всех сразу'''
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        if number_test:
            sel = cur.execute(f"UPDATE tests SET open=True WHERE code={number_test};")
        else:
            sel = cur.execute(f"UPDATE tests SET open=True WHERE class<>0;")
        self.con.commit()
        self.con.close()
        return f"Тест{f' {number_test} открыт' if number_test else 'ы все открыты'} для доступа"

    def close_test_db(self, number_test=False):
        '''метод закрытия для выполнения теста путем изменения флага одного или всех сразу'''
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        if number_test:
            sel = cur.execute(f"UPDATE tests SET open=False WHERE code={number_test};")
        else:
            sel = cur.execute(f"UPDATE tests SET open=False WHERE class<>0;")
        self.con.commit()
        self.con.close()
        return f"Тест{f' {number_test} закрыт' if number_test else 'ы все закрыты'} для доступа"

    def list_test_db(self):
        '''метод формирует полный список тестов находящихся в базе данных'''
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        sel = cur.execute(f"SELECT code, open, subject FROM tests").fetchall()
        self.list_of_topics = [str(i[0]) + ' ' + ('Open' if i[1] else 'Close') + ' ' + str(i[2]) + '\n' for i in
                               sorted(list(set([i for i in sel])))]
        self.con.close()
        return ''.join(self.list_of_topics)

    def the_test_is_open(self, number_test):
        '''метод проверяет доступность для выполнения теста'''
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        try:
            sel = cur.execute(f"SELECT open FROM tests WHERE code={number_test}").fetchone()[0]
        except TypeError:
            sel = False
        self.con.close()
        return sel

# dd = VkBot(21312)
# print('проверка теста', dd.the_test_is_open(701))
