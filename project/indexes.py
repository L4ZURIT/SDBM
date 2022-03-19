import sys
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from sqlalchemy import Table


sys.path.insert(1, './')
from project.sql import sqlm
from project.request import Request



# Данные классы должны были использоваться для продвинутого редактирования свойств полей, но пока разработка этого механизма отложена и появится в следующих обновлениях
"""
class CustomComboBox(QComboBox):
    def __init__(self, tw, text, row, col) -> None:
        super().__init__()
        self.tw:QTableWidget = tw
        self.row = row
        self.col = col
        self.setEditable(True)
        self.wheelEvent = self.my_wheel
        self.currentTextChanged.connect(self.my_change)
        

    def my_wheel(self, e):
        pass

    def my_change(self):
        self.tw.cellChanged.emit(self.row, self.col)

class DataTypeComboBox(CustomComboBox):
    def __init__(self, tw, text, row, col) -> None:
        super().__init__( tw, text, row, col)
        self.addItems([
            "INT(Size)",
            "INT UNSIGNED(Size)",
            "INTEGER(Size)",
            "TINYINT(Size)",
            "TINYINT UNSIGNED(Size)",
            "SMALLINT(Size)",
            "SMALLINT UNSIGNED(Size)",
            "MEDIUMINT(Size)",
            "MEDIUMINT UNSIGNED(Size)",
            "BIGINT(Size)",
            "BIGINT UNSIGNED(Size)",
            "FLOAT(M,D)",
            "FLOAT(M,D) UNSIGNED",
            "DOUBLE(M,D)",
            "DOUBLE(M,D) UNSIGNED",
            "REAL(M,D)",
            "DOUBLE PRESICION(M,D)",
            "DECIMAL(M,D)",
            "DECIMAL(M,D) UNSIGNED",
            "DEC(M,D)",
            "NUMERIC(M,D)",
            "CHAR(Size)",
            "CHARACTER(Size)",
            "BINARY(Size)",
            "VARCHAR(Size)",
            "CHARACTER VARYING(Size)",
            "VARBINARY(Size)",
            "TEXT",
            "TINYTEXT",
            "MEDIUMTEXT",
            "LONGTEXT",
            "BLOB",
            "TINYBLOB",
            "MEDIUMBLOB",
            "LONGBLOB",
            "ENUM",
            "SET",
            "DATE",
            "DATETIME",
            "TIMESTAMP",
            "TIME",
            "YEAR(Size)"
        ])
        self.setCurrentText(text)

class DefaultComboBox(CustomComboBox):
    def __init__(self, tw, text, row, col) -> None:
        super().__init__( tw, text, row, col)
        self.addItems(["None", "NULL"          
        ])
        self.setCurrentText(text)

"""      

class Indexes():
    def __init__(self, main:QMainWindow):
        # Переменные 
        self.main:QMainWindow = main
        self.tw_indexes:QTableWidget = main.tw_indexes
        # reinstall
        self.sql:sqlm = main.sqlm
        self.table_name:str = None
        self.alch_table:Table = None
        # - - -

        # Настройка интерфейса 
        self.InitTable()

        # - - -

        # Связка сигналов 
        #self.tw_indexes.cellChanged.connect(self.edit)

        # - - - 

    def InitTable(self):
        pass


    def edit(self, row, col):
        print(row, col)



    def open_table(self, item:QListWidgetItem, alch_table):

        # Блокируем редактирование, чтобы свойства можно было только просматривать
        self.tw_indexes.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tw_indexes.setRowCount(0)

        self.table_name = item.text()

        # Инициализация класса таблицы SQLAlchemy
        self.alch_table = alch_table

        # reinstall
        keys = list(self.sql.get_table(self.alch_table).keys())

        self.tw_indexes.setRowCount(len(keys))

        


        # Ждет своего часа когда у приложения появится функция редактирования атрибутов
        """
        for row in range(len(keys)):
            self.tw_indexes.setIndexWidget(
                self.tw_indexes.model().index(row, 2), 
                DataTypeComboBox(
                    self.tw_indexes,
                    str(self.alch_table.columns[keys[row]].type), 
                    row, 
                    2
                    ))

        for row in range(len(keys)):
            self.tw_indexes.setIndexWidget(
                self.tw_indexes.model().index(row, 3), 
                DefaultComboBox(
                    self.tw_indexes,
                    str(self.alch_table.columns[keys[row]].default), 
                    row, 
                    2
                    ))

                    """

        # Заполнение свойств полей в виджет отображения 

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 0, QTableWidgetItem(keys[row]))
            
        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 1, QTableWidgetItem(str(self.alch_table.columns[keys[row]].type)))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 2, QTableWidgetItem(str(self.alch_table.columns[keys[row]].default)))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 3, QTableWidgetItem(str(self.alch_table.columns[keys[row]].comment)))
            
        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 4, QTableWidgetItem(str(self.alch_table.columns[keys[row]].unique.__bool__())))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 5, QTableWidgetItem(str(self.alch_table.columns[keys[row]].autoincrement)))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 6, QTableWidgetItem(str(self.alch_table.columns[keys[row]].primary_key)))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 7, QTableWidgetItem(str([k for k in self.alch_table.columns[keys[row]].foreign_keys])))

        for row in range(len(keys)):
            self.tw_indexes.setItem(row, 8, QTableWidgetItem(str([k for k in self.alch_table.columns[keys[row]].constraints])))
        