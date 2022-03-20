from datetime import date, datetime, time, timedelta
from xmlrpc.client import MAXINT
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import pandas as pd

from sqlalchemy import *

sys.path.insert(1, './')
from project.sql import sqlm
from project.request import Request



class ed():
    class _int(QSpinBox):
        def __init__(self, value, parent=None):
            super().__init__(parent)
            self.setValue(value)

        


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
        self.sql:sqlm = main.sqlm
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
        tables = self.sql.engine.table_names()
        print(tables)
        for table in tables:
            self.lw_tables.addItem(str(table))

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
            self.req.go(req)
        except ValueError:
            mes = QMessageBox.critical(self.main, "aa", "ss")

        self.open_table(QListWidgetItem(self.table_name), self.alch_table)
        

    def get_row(self, row):
        ans = []
        
        for col in range(1, self.tw_content.columnCount()):
            if type(self.tw_content.item(row, col)) is QTableWidgetItem and self.tw_content.item(row, col).text() != "None":
                ans.append(self.tw_content.item(row, col).text())
            else:
                ans.append(None)
        return ans



    def get_header(self):

        ans = []
        for col in range(1, self.tw_content.columnCount()):
            ans.append(self.tw_content.horizontalHeaderItem(col).text())
        return ans


    def open_table(self, item:QListWidgetItem, alch_table):

        self.main.stack_main.setCurrentIndex(1)
        self.tw_content.clear()
        self.table_name = item.text()
        # инициализируем содержимое выбранной таблицы сохраняя экземпляр SQLalchemy
        
        self.alch_table = alch_table
        self.dict_table = self.sql.get_table(self.alch_table)
            
        print(self.dict_table, " - ", type(self.dict_table))

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
                    # if isinstance(values[col][row], int):
                    #     self.tw_content.setIndexWidget(self.tw_content.model().index(row,col+1), ed._int(values[col][row]))
                    
                    

            # Наполняем первый столбец интерактивными кнопками
            for row in range(self.tw_content.rowCount()):
                self.tw_content.setIndexWidget(self.tw_content.model().index(row, 0), ButtonForRow(self.initiate_status(row, len(values[0])), row, self.MethodForButton, self.tw_content.cellChanged))

            self.tw_content.setEditTriggers(QAbstractItemView.AllEditTriggers)

        else:

            self.tw_content.setColumnCount(len(keys))
            self.tw_content.setRowCount(len(values[0]))

            for col in range(len(keys)):
                self.tw_content.setHorizontalHeaderItem(col, QTableWidgetItem(str(keys[col])))
                print()
                for row in range(len(values[col])):
                    self.tw_content.setItem(row, col, QTableWidgetItem(str(values[col][row])))
                    print(str(values[col][row]), " - " ,type(values[col][row]))

            self.tw_content.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row in range(self.tw_content.rowCount()):
            self.tw_content.showRow(row)


        if self.cb_hide_row_indexes.isChecked():
            self.tw_content.verticalHeader().hide()
        else:
            self.tw_content.verticalHeader().show()


    # Устанвка статуса для кнопки на кортеже
    def initiate_status(self, row:int, max:int):

        if row < max:
            return 0
        elif row == max:
            return 2
        else:
            return 3



        

                
            


