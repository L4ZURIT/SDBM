import itertools
import json
import sys
import pymysql
import pandas as pd
import numpy as np

from datetime import date, datetime, time, timedelta

from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Query



sys.path.insert(1, './')

def render_query(statement, dialect=None):
    """
    Generate an SQL expression string with bound parameters rendered inline
    for the given SQLAlchemy statement.
    WARNING: This method of escaping is insecure, incomplete, and for debugging
    purposes only. Executing SQL statements with inline-rendered user values is
    extremely insecure.
    Based on http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query
    """
    if isinstance(statement, Query):
        if dialect is None:
            dialect = statement.session.bind.dialect
        statement = statement.statement
    elif dialect is None:
        dialect = statement.bind.dialect

    class LiteralCompiler(dialect.statement_compiler):

        def visit_bindparam(self, bindparam, within_columns_clause=False,
                            literal_binds=False, **kwargs):
            return self.render_literal_value(bindparam.value, bindparam.type)

        def render_array_value(self, val, item_type):
            if isinstance(val, list):
                return "{%s}" % ",".join([self.render_array_value(x, item_type) for x in val])
            return self.render_literal_value(val, item_type)

        def render_literal_value(self, value, type_):
            if isinstance(value, int):
                return str(value)
            elif isinstance(value, (str, date, datetime, timedelta)):
                return "'%s'" % str(value).replace("'", "''")
            elif isinstance(value, list):
                return "'{%s}'" % (",".join([self.render_array_value(x, type_.item_type) for x in value]))
            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return LiteralCompiler(dialect, statement).process(statement)

class sqlm():
    @staticmethod
    def j_read() -> dict:
        with open("data/database.json") as json_file:
            data = json.load(json_file)
        return data

    def __init__(self) -> None:
        self.engine = create_engine(URL.create(**mysql_m.j_read()))
        self.md = MetaData(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.alch_table = Table("книги", self.md, autoload_with=self.engine)
        for it in  self.session.query(self.alch_table):
            print(it)


    def request(self, req:str):
        self.Connect()
        try:
            self.cur.execute(str(req))
            self.con.commit()
        except Exception as ex:
            return ex
        return self.cur.fetchall()


        """
        
        ИСПРАВИТЬ МЕНЕДЖЕР БАЗ ДАННЫХ И ЗАМЕНИТЬ НА ИНСТРУМЕНТЫ SQLALCHEMY
        
        """



# Класс предназначен для подключения к сервисам Mysql и работы с таблицами в этой базе
class mysql_m():


    @staticmethod
    def j_read() -> dict:
        with open("data/database.json") as json_file:
            data = json.load(json_file)
        return data


    def __init__(self, send = True) -> None:
        self.Read()
        self.Connect()
        self.cur.execute("SELECT VERSION()")
        print("Подключение к сервисам MYSQL успешно, версия базы -", self.cur.fetchone()[0])

        # переключатель которые в зависимости от положения заставляет методы работать по разному:
            # True - метод производит запрос и возвращает ответ от сервера
            # False - метод возвращает сконструированный запрос SQL
        self.send = send

    def SetSend(self, how:bool):
        self.send = how

    # Метод считывает информацию для подключения к базе данных и инициализирует поля для дальнейшей работы
    def Read(self):
        with open("data/database.json", 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.host = content["host"]
            self.user = content["username"]
            self.secret = content["password"]
            self.db = content["database"]

    # Проверка наличия информации о подключаемой базе в конфигурационных файлах приложения 
    def CheckCfg(self):
        if (self.host == '' or
            self.user == '' or
            self.db == ''):
            return False
        else:
            return True

    # Подключение к базе и инициализация главных инструментов для работы с сервером 
    def Connect(self):
        if self.CheckCfg():
            try:
                self.con = pymysql.connect(
                    host=self.host, 
                    user= self.user, 
                    password=self.secret, 
                    database=self.db
                )
            except Exception as ex:
                print("Не удалось подключится к сервисам MYSQL Код ошибки:", str(ex))
                return 0
            self.cur = self.con.cursor()
        else:
            print("Не заданны данные для подключения к базе")

        pass

    # позволяет передать собственный запрос и получить результат
    def request(self, req:str):
        self.Connect()
        try:
            self.cur.execute(str(req))
            self.con.commit()
        except Exception as ex:
            return ex
        return self.cur.fetchall()


    # возвращает кортеж с информацией (кортеж: название + тип таблицы) об отношениях в базе. По желанию можно дополнить запрос в параметре extra
    def get_tables(self, extra = ""):
        self.Connect()
        req = """ SHOW FULL TABLES """ + extra
        if self.send:
            self.cur.execute(req)
            return self.cur.fetchall()
        else:
            return req

    # создает новую таблицу, нужно указать новое название с учетом, что оно не должно быть идентично с каким-либо названием таблицы из базы
    # в параметре columns необходимо передать словарь с уникальными названиями полей в качестве ключей и указанием их типов в качестве значений
    # если вы не готовы внести информацию о полях отношения, функция по умолчанию определит идентификатор, необходимо учитывать это при дальнейшей модификации отношения
    def new_table(self, t_name, columns = {"id":"INT AUTO_INCREMENT PRIMARY KEY"}):
        self.Connect()
        col_t = "("
        for col in columns:
            col_t += col + " " + columns[col] + ","
        req = """CREATE TABLE {name} {cols}""".format(name = t_name, cols = col_t[:-1])+")"
        if self.send:
            try:  
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

    # переименовывает отношение
    def rename_table(self, old_name, new_name):
        self.Connect()
        req = """
                    ALTER TABLE {on} RENAME TO {nn}
                """.format(on = old_name, nn = new_name)
        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req
        


    # удаляет отношение
    def delete_table(self, table):
        self.Connect()
        req = """
                    DROP TABLE {on}
                """.format(on = table)
        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req


    # удаляет множество кортежей отношения
    def clear_table(self, table):
        self.Connect()
        
        req = """TRUNCATE TABLE {on}""".format(on = table)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

    #  добавляет новое поле отношения 
    def new_column(self, new_column, table_name):
        self.Connect()

        req = """ALTER TABLE {tn} ADD {nc}""".format(tn = table_name, nc = new_column)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

        

    # удаляет необходимое поле отношения
    def delete_column(self, column, table):
        self.Connect()

        req = """ ALTER TABLE {tn} DROP COLUMN {nc} """.format(tn = table, nc = column)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

        

    # переименовывает имеющиесе поле отношения
    def rename_column(self, old_column, new_column, table):
        self.Connect()

        req = """
                    ALTER TABLE {tn} CHANGE {on} {nc}
                """.format(tn = table, on = old_column, nc = new_column)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

    def delete_row(self, table, indexes:list, values:list):

        if len(indexes) != len(values):
            raise NameError(" lengths of lists unequal")

        self.Connect()

        req = "DELETE FROM %s WHERE"%(table)

        for i, v in zip(indexes, values):
            req += " %s = %s AND"%(i, v)

        req = req[:-3]

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req

        

    # Добавить инструменты для работы с именоваными и неимнованными ограничениями уникальности

    # Добавить инструменты дял работы с внешними ключами и связями таблицы



    # позволяет добавить новые множества кортежей в имеющиесе отношение
    # необходимо в качестве данных передавать словарь с именами полей в качестве ключей и списками значений в качестве значений словаря
    # в любом случае необходимо передавать данные именно указанным выше способом, т.е. даже если у вас всего один элемент, необходимо обернуть его в список
    # в случае если данные списки будут обладать разной длинной, недостающие значения заменятся на None
    def insert_into(self, table, data:dict):
        self.Connect()
        columns = ', '.join("`" + str(x) + "`" for x in data.keys())
        vals = list(map(list, itertools.zip_longest(*data.values(), fillvalue=None)))
        values = ", ".join("("+", ".join(str(val[i]) if type(val[i]) != str else "'"+val[i]+"'" for i in range(len(val)))+")" for val in vals)
        req = "INSERT INTO %s ( %s ) VALUES %s;" % (table, columns, values)
        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req


    # позволяет получить все отношение целиком
    def get_table(self, table):
        self.Connect()

        req = "SELECT * FROM %s"%(table)

        if self.send:
            try:
                tab = pd.read_sql(req, self.con)
                ans = tab.to_dict(orient='list')
                self.con.commit()
                return ans
            except Exception as e:
                print(e)
                return e
        else:
            return req


    # позволяет получить все отношение целиком
    def find_primary_key(self, table):
        self.Connect()

        req = "SELECT C.COLUMN_NAME FROM information_schema.table_constraints AS pk INNER JOIN information_schema.KEY_COLUMN_USAGE AS C ON C.TABLE_NAME = pk.TABLE_NAME AND C.CONSTRAINT_NAME = pk.CONSTRAINT_NAME AND C.TABLE_SCHEMA = pk.TABLE_SCHEMA WHERE  pk.TABLE_NAME  = '{table_}' AND pk.TABLE_SCHEMA = '{database}' AND pk.CONSTRAINT_TYPE = 'PRIMARY KEY'".format(table_ = table, database = self.db)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req


    # позволяет получить все отношение целиком
    def find(self, table, what):
        self.Connect()

        req = "SELECT C.COLUMN_NAME FROM information_schema.table_constraints AS pk INNER JOIN information_schema.KEY_COLUMN_USAGE AS C ON C.TABLE_NAME = pk.TABLE_NAME AND C.CONSTRAINT_NAME = pk.CONSTRAINT_NAME AND C.TABLE_SCHEMA = pk.TABLE_SCHEMA WHERE  pk.TABLE_NAME  = '{table_}' AND pk.TABLE_SCHEMA = '{database}' AND pk.CONSTRAINT_TYPE = '{type_}'".format(table_ = table, database = self.db, type_ = what)

        if self.send:
            try:
                self.cur.execute(req)
            except Exception as e:
                print(e)
                return e
            self.con.commit()
        else:
            return req


        


if __name__ == "__main__":
    
    s = sqlm()
     