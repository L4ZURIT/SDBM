from datetime import date, datetime, time, timedelta
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import pandas as pd

from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Query

sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request


# взято с сайта https://question-it.com/questions/1490148/sqlalchemy-vyvesti-fakticheskij-zapros
# специальный метод конструктора выражений правильно работающий с датой и временем (НАДО ГРАМОТНО ОФОРМИТЬ)
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



# Класс описывающий кнорки взаимодействия с кортежами в отношении
# Эти кнопки заполняют первый (получается неиспользуемый самой бд) столбец и служат для взаимодействия с кортежем, который находится
# на одной строке с этой кнопкой. У кнопки есть несколько состояний:
# - Удалить: в таком положении кнопка находится когда кортеж введеный в таблицу отображения (Имеется ввиду объект интерфейса QTablewidget) никак не был изменен пользователем с момента появления на экране. При нажатии на кнопку происходит удаление кортежа, выполняется соответствующий запрос к бд, но перед этим конечно же у пользователя необходимо спросить уверен ли он в своих действиях и предложить ему написать запрос в строку запросов (QGroupBox с подписью SQL внизу интерфейса приложения), такое уточнение осуществляется с использованием QMessageBox
# - Обновить: в таком положении кнопка оказывается, когда представленные данные были измененны в пользовательском виджете, однако изменения еще никак не отобразились в бд. При нажатии необходимо спросить у пользоваетеля, хочет ли он применить или отменить изменения
# - Добавить: в таком положении кнопка отображается на пустой строке, у пользователя есть возможность добавить новые данные в первую свободную строчку после списка кортежей. 
# - Неактивна: так как у пользователя нет возможности добавить новый кортеж в то место которое ему вздумается, то и остальные поля будут недоступны пока не заполнена первая свободная строчка отношения
class ButtonForRow(QPushButton):

    def __init__(self, state, index, slot, signal, parent=None):
        super().__init__(parent)

        # инициализация переменных 
        self.state = state
        self.index = index
        self.slot = slot
        # - - - 

        # связка сигналов 
        self.clicked.connect(self.send_self)
        signal.connect(self.change_button_state)
        #
        # - - - 
        if state == 0: # Удалить 
            self.setText("-")
            pass
        elif state == 1: # Обновить 
            self.setText("R")
            pass
        elif state == 2: # Добавить
            self.setText("+")
            pass
        elif state == 3: # Пустая
            self.setText("")
            self.setEnabled(False)
            pass

    # Реализация метода, который вызывается при нажатии на кнопку описан в родительском классе Tables и называется MethodForButton
    def send_self(self):
        self.slot(self)

    def change_button_state(self, row, column):
        if (self.index == row and self.state == 0):
            self.state = 1
            self.setText("R")
        pass




        


class Tables():
    def __init__(self, main:QMainWindow) -> None:

        # Инициализация переменных
        self.st = main.standart
        self.lw_tables:QListWidget = main.lw_tables
        self.tw_content:QTableWidget = main.tw_content
        self.sql:mysql_m = main.sql
        self.req:Request = main.req
        self.table_name:str = None
        self.main:QMainWindow = main
        self.cb_write_mode:QCheckBox = main.cb_write_mode
        self.tb_content:QToolButton = main.tb_content
        self.spl_content:QSplitter = main.spl_content
        self.gb_properties:QGroupBox = main.gb_properties
        self.pb_hide_settings:QPushButton = main.pb_hide_settings
        self.pb_hide_properties:QPushButton = main.pb_hide_properties
        self.pb_settings_apply:QPushButton = main.pb_settings_apply
        self.cb_hide_row_indexes:QCheckBox = main.cb_hide_row_indexes
        
        
        # Настройка интерфейса
        self.spl_content.hide()
        self.gb_properties.hide()
        self.TablesListInit()
        self.TablesInterfaceInit()

        # ---


        # Связка сигналов
        
        self.pb_hide_properties.clicked.connect(self.gb_properties.hide)
        self.pb_hide_settings.clicked.connect(self.spl_content.hide)
        self.pb_settings_apply.clicked.connect(self.reload_content)
        # ---

        # Переопределение событий
        

        # ---
        

    def TablesListInit(self):
        # reinstall
        tables = self.sql.request(self.sql.get_tables())
        for table in tables:
            self.lw_tables.addItem(str(table[0]))

    def TablesInterfaceInit(self):
        menu = QMenu(self.tb_content)
        act1 = menu.addAction("Настройки")
        act2 = menu.addAction("Обновить данные")
        act3 = menu.addAction("Отменить изменения")
        act4 = menu.addAction("Свойства поля")

        act1.triggered.connect(self.spl_content.show)
        act2.triggered.connect(self.reload_content)
        act3.triggered.connect(self.reload_content)
        act4.triggered.connect(self.gb_properties.show)

        self.tb_content.setPopupMode(QToolButton.InstantPopup)
        self.tb_content.setMenu(menu)
        

    
    def reload_content(self):
        if self.table_name == None:
            mes = QMessageBox.critical(self.main, "Ошибка обновления", "Нет выбранной таблицы для обновления")
        else:
            self.open_table(QListWidgetItem(self.table_name), self.alch_table)



    def MethodForButton(self, button:ButtonForRow):

        h = self.get_header()
        r = self.get_row(button.index)
        

        if button.state == 0: # удалить          
            req = self.alch_table.delete().where(
                and_(
                    self.alch_table.c[i.name] == self.dict_table[i.name][button.index] 
                    for i in self.alch_table.primary_key.columns
                    ))
            self.tw_content.hideRow(button.index)


        elif button.state == 1: # обновить
            req = self.alch_table.update().where(
                and_(
                    self.alch_table.c[i.name] == self.dict_table[i.name][button.index] 
                    for i in self.alch_table.primary_key.columns
                    )
                    ).values(tuple(r[j]
                    for j in range(len(self.alch_table.columns))))
            
            
        elif button.state == 2: # добавить
            req = self.alch_table.insert().values(tuple(r[j] 
                    for j in range(len(self.alch_table.columns))))
        else:
            return 
            
        try:
            self.req.go(render_query(req))
        except ValueError:
            mes = QMessageBox.critical(self.main, "aa", "ss")

        self.open_table(QListWidgetItem(self.table_name), self.alch_table)
        

    def get_row(self, row):
        ans = []
        
        for col in range(1, self.tw_content.columnCount()):
            if type(self.tw_content.item(row, col)) is QTableWidgetItem:
                ans.append(self.tw_content.item(row, col).text())
            else:
                ans.append('')
        return ans



    def get_header(self):

        ans = []
        for col in range(1, self.tw_content.columnCount()):
            ans.append(self.tw_content.horizontalHeaderItem(col).text())
        return ans


    def open_table(self, item:QListWidgetItem, alch_table):

        self.main.stack_main.setCurrentIndex(1)
        

        self.tw_content.clear()

        # переключаем состояние методов менеджера sql на мгновенное выполнение
        # reinstall
        self.sql.SetSend(True)

        self.table_name = item.text()
        # инициализируем содержимое выбранной таблицы сохраняя экземпляр SQLalchemy
        # reinstall
        self.dict_table = self.sql.get_table(self.table_name)
        self.alch_table = alch_table

        
        

        # Словарь значений отношения
        keys = list(self.dict_table.keys())
        values = list(self.dict_table.values())


        # Первоначальная настройка интерфейса таблицы с установлением количества колонок и их размером
        self.tw_content.setHorizontalHeaderItem(0, QTableWidgetItem(""))
        self.tw_content.setColumnWidth(0, 32)
        self.tw_content.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        if self.cb_write_mode.isChecked():
            
            # Здесь хотелось бы в дальнейшем усовершенствовать таблицу таким образом чтобы вводимые в ней виджеты отображались в соответсвии с типом данных

            # Устанавливаем содержимое таблицы с соответсвующими типами данных
            # for col in range(len(keys)):
            #     self.tw_content.setHorizontalHeaderItem(col+1, QTableWidgetItem(str(keys[col])))
            #     for row in range(len(values[col])):
            #         if self.alch_table.columns[keys[col]].type.python_type == date:
            #             self.tw_content.setIndexWidget(self.tw_content.model().index(row, col+1), QDateEdit(date=values[col][row]))
            #         elif self.alch_table.columns[keys[col]].type.python_type == time:
            #             self.tw_content.setIndexWidget(self.tw_content.model().index(row, col+1), QTimeEdit(time=values[col][row]))
            #         elif self.alch_table.columns[keys[col]].type.python_type == datetime:
            #             self.tw_content.setIndexWidget(self.tw_content.model().index(row, col+1), QDateTimeEdit(datetime==values[col][row]))
            #         else:
            #             self.tw_content.setItem(row, col+1, QTableWidgetItem(str(values[col][row])))

            self.tw_content.setColumnCount(len(keys)+1)
            self.tw_content.setRowCount(len(values[0])+1)

            for col in range(len(keys)):
                self.tw_content.setHorizontalHeaderItem(col+1, QTableWidgetItem(str(keys[col])))
                for row in range(len(values[col])):
                    self.tw_content.setItem(row, col+1, QTableWidgetItem(str(values[col][row])))

            # Наполняем первый столбец интерактивными кнопками
            for row in range(self.tw_content.rowCount()):
                self.tw_content.setIndexWidget(self.tw_content.model().index(row, 0), ButtonForRow(self.initiate_status(row, len(values[0])), row, self.MethodForButton, self.tw_content.cellChanged))

            self.tw_content.setEditTriggers(QAbstractItemView.AllEditTriggers)

        else:

            self.tw_content.setColumnCount(len(keys))
            self.tw_content.setRowCount(len(values[0]))

            for col in range(len(keys)):
                self.tw_content.setHorizontalHeaderItem(col, QTableWidgetItem(str(keys[col])))
                for row in range(len(values[col])):
                    self.tw_content.setItem(row, col, QTableWidgetItem(str(values[col][row])))

            self.tw_content.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row in range(self.tw_content.rowCount()):
            self.tw_content.showRow(row)


        if self.cb_hide_row_indexes.isChecked():
            self.tw_content.verticalHeader().hide()
        else:
            self.tw_content.verticalHeader().show()

        # reinstall
        self.sql.SetSend(self.st)


    # Устанвка статуса для кнопки на кортеже
    def initiate_status(self, row:int, max:int):

        if row < max:
            return 0
        elif row == max:
            return 2
        else:
            return 3



        

                
            


