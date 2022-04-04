import random
import sqlite3


class TestSys:
    items = []

    def __init__(self, n):
        self.n = n
        self.result = 0
        #self.user = user_t
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        try:
            self.id_test = cur.execute(f"SELECT id_test FROM tests WHERE code = {self.n}").fetchone()[0]
            self.name_test = cur.execute(f"SELECT subject FROM tests WHERE code = {self.n}").fetchone()[0]
            self.id_q = [i[0] for i in cur.execute(f"SELECT id_q FROM question WHERE id_t={self.id_test}").fetchall()]
        except TypeError:
            self.id_test = False
            self.name_test = 'Такого теста нет'
            self.id_q = False
        random.shuffle(self.id_q)  # Можно перемешать вопросы теста
        print(self.id_test)  # id теста в базе вопросов
        print(self.id_q)  # Список вопросов для данного теста
        self.con.close()
        self.name_test = self.name_test + f"{len(self.id_q):2}"
        print('Тест сформирован', self.id_test)

    def testing(self):
        '''Готовим список по данному тесту, который состоит из вопроса,
        картинки к вопросу, ответы и правильный ответ.
        Берем последний вопрос из списка вопросов'''
        if self.id_q:
            self.t_n = self.id_q.pop(0)
        else:
            return False, False, self.result, self.name_test
        #print(self.t_n)
        self.con = sqlite3.connect('physics.db')
        cur = self.con.cursor()
        self.id_question = [i for i in cur.execute(
            f"SELECT answer, question, picture, a1, a2, a3, a4, a5 FROM question WHERE id_q = {self.t_n}").fetchall()[0]]
        self.ans = self.id_question[0]
        self.id_question = self.id_question[1:]
        #print(self.id_question)
        self.con.close()
        return self.id_question, True, self.result, self.name_test










#Test_sys(703).testing()
