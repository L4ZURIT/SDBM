import json
import sys
import pymysql
import pandas as pd

sys.path.insert(1, './')



# Класс предназначен для подключения к сервисам Mysql и работы с таблицами в этой базе
class mysql_m():
    def __init__(self) -> None:
        self.Read()
        self.Connect()
        self.cur.execute("SELECT VERSION()")
        print("Подключение к сервисам MYSQL успешно, версия базы -", self.cur.fetchone()[0])
        pass

    

    # Метод считывает информацию для подключения к базе данных и инициализирует поля для дальнейшей работы
    def Read(self):
        with open("data/database.json", 'r', encoding='utf-8') as f:
            content = json.load(f)
            self.host = content["host"]
            self.user = content["user"]
            self.secret = content["secret"]
            self.db = content["db"]

    # Проверка заполнения информации о подключаемой базе
    def CheckCfg(self):
        if (self.host == '' or
            self.user == '' or
            self.secret == '' or 
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


    def get_tables(self):
        self.Connect()
        self.cur.execute("""
            SHOW FULL TABLES
        """)
        return self.cur.fetchall()


    def get_tables_like(self, what):
        self.Connect()
        self.cur.execute("""
            SHOW FULL TABLES LIKE '{what_}'
        """.format(what_ = what))
        return self.cur.fetchall()


    def new_table(self, t_name, columns = {"id":"INT AUTO_INCREMENT PRIMARY KEY"}):
        self.Connect()
        col_t = "("
        for col in columns:
            col_t += col + " " + columns[col] + ","
        try:
            self.cur.execute("""
                CREATE TABLE {name} {cols}
            """.format(name = t_name, cols = col_t[:-1])+")")
        except Exception as e:
            print(e)
            return e
        self.con.commit()


    def rename_table(self, old_name, new_name):
        self.Connect()
        try:
            self.cur.execute("""
                ALTER TABLE {on} RENAME TO {nn}
            """.format(on = old_name, nn = new_name))
        except Exception as e:
            print(e)
            return e
        self.con.commit()

    def delete_table(self, table):
        self.Connect()
        try:
            self.cur.execute("""
                DROP TABLE {on}
            """.format(on = table))
        except Exception as e:
            print(e)
            return e
        self.con.commit()


    def clear_table(self, table):
        self.Connect()
        try:
            self.cur.execute("""
                TRUNCATE TABLE {on}
            """.format(on = table))
        except Exception as e:
            print(e)
            return e
        self.con.commit()

        
    def new_column(self, new_column, table_name):
        self.Connect()
        try:
            self.cur.execute("""
                ALTER TABLE {tn} ADD {nc}
            """.format(tn = table_name, nc = new_column))
        except Exception as e:
            print(e)
            return e
        self.con.commit()

    def delete_column(self, column, table):
        self.Connect()
        try:
            self.cur.execute("""
                ALTER TABLE {tn} DROP COLUMN {nc}
            """.format(tn = table, nc = column))
        except Exception as e:
            print(e)
            return e
        self.con.commit()

    def rename_column(self, old_column, new_column, table):
        self.Connect()
        try:
            self.cur.execute("""
                ALTER TABLE {tn} CHANGE {on} {nc}
            """.format(tn = table, on = old_column, nc = new_column))
        except Exception as e:
            print(e)
            return e
        self.con.commit()

    # Добавить инструменты для работы с именоваными и неимнованными ограничениями уникальности

    # Добавить инструменты дял работы с внешними ключами и связями таблицы

    



    



if __name__ == "__main__":
    sql = mysql_m()
    sql.delete_table("test_1")
    print(sql.get_tables())
    