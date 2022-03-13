from datetime import date, datetime, time

from faker import Faker

import sys
import json
import random
import pickle

from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from sqlalchemy import Table


sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request
from test import human


def read_dbg():
    with open("data/database_generators.pkl", "rb") as file:
        data = pickle.load(file)
    return data

def write_dbg(data):
    with open("data/database_generators.pkl", "wb") as file:
        pickle.dump(data, file)


# Установка генератора
def set_generator(database, table, column, generator):
    geneartors = read_dbg()
    # Возможно здесь появится KEYerror при добавлении новой таблицы в базу, тогда метод не найдет параметр table и его надо будет установить
    geneartors[database][table][column] = generator
    write_dbg(geneartors)
    


# Генератор для значений вводимых вручную
class manual():
    values:list = None
    def __init__(self, values:list) -> None:
        self.values = values

    def generate_random(self, count:int) -> list:
        return random.choices(self.values, count)

    def generate_unique(self, count:int) -> list:
        return random.sample(self.values, count)


# Виджет генератора для ФИО 
class FIO(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.cb_male = QCheckBox("Мужские")
        self.cb_female = QCheckBox("Женские")
        self.layout().addWidget(self.cb_male)
        self.layout().addWidget(self.cb_female)
        self.layout().setContentsMargins(0,0,0,0)


# Класс слота генератора в виджете визуализации списка генераторов 
class moded_item(QListWidgetItem):
    def __init__(self, name, description, var_list, edit, widget) -> None:
        super().__init__()
        self.setText(name)
        self.description = description
        self.var_list = var_list
        self.edit = edit
        try:
            # Инициализация виджета настроек генератора
            self.widget = eval(widget)()
        except TypeError:
            print("У генератора '%s' не настроен виджет параметров"%name)
            self.widget = QLabel("")



# Инициализирующий класс модуля генераторов
class Generator():

    def __init__(self, main:QMainWindow) -> None:
        # Переменные
        self.main:QMainWindow = main
        self.alch_table:Table = None
        self.lw_columns:QListWidget = main.lw_columns
        self.lbl_datatype:QLabel = main.lbl_datatype
        self.sw_generator:QStackedWidget = main.sw_generator
        self.gb_parametres:QGroupBox = main.gb_parametres
        self.te_values:QTextEdit = main.te_values
        self.lw_generators:QListWidget = main.lw_generators
        self.lo_for_generator:QLayout = main.lo_for_generator
        self.lbl_own_values_count:QLabel = main.lbl_own_values_count
        self.lbl_datatype_warning:QLabel = main.lbl_datatype_warning
        self.pb_save_generator:QPushButton = main.pb_save_generator
        self.sb_cortages:QSpinBox = main.sb_cortages
        self.tb_find_generator:QToolButton = main.tb_find_generator
        self.selected_column:str = None
        self.selected_datatype:type = None


        # установленные значения для столбца
        self.list_of_values_for_col:list = []
        # установленные наборы значений для таблицы
        self.dict_of_list_with_values:dict = {}


        self.ToolButtonInit()
                
        
        # Связка сигналов
        
        self.lw_columns.itemDoubleClicked.connect(self.select_column)
        self.te_values.textChanged.connect(self.get_own_var_from_te)
        self.pb_save_generator.clicked.connect(self.set_generator)
        self.lw_generators.itemClicked.connect(self.show_params)
        # 
        self.sw_generator.setCurrentIndex(2)


    # Инициализация кнопки раскрывающегося списка для работы с генераторами
    def ToolButtonInit(self):
        menu = QMenu(self.tb_find_generator)
        act1 = menu.addAction("Установить генератор")
        act2 = menu.addAction("На основе данных столбца")
        act3 = menu.addAction("Редактор значений")
        act4 = menu.addAction("Помощь")

        act1.triggered.connect(self.get_back)
        act2.triggered.connect(self.set_other_var)
        act3.triggered.connect(self.set_own_var)
        #act4.triggered.connect(self.)

        self.tb_find_generator.setPopupMode(QToolButton.InstantPopup)
        self.tb_find_generator.setMenu(menu)
        
    # Инициализация листвиджета со списком генераторов на пользовательском интерфейсе
    def InitLwGenerators(self, dtype):
        self.lw_generators.clear()
        with open("data/generator.json", encoding="utf-8") as json_file:
            dict_generators = json.load(json_file)
        try:
            for item in dict_generators[dtype]:
                self.lw_generators.addItem(
                    moded_item(
                        dict_generators[dtype][item]["name"], 
                        dict_generators[dtype][item]["description"], 
                        dict_generators[dtype][item]["var_list"], 
                        dict_generators[dtype][item]["edit"], 
                        dict_generators[dtype][item]["widget"]))
        except KeyError:
            self.lw_generators.addItem(QListWidgetItem("Для выбранного типа данных, не существует генератора"))
            

    # инициализация модуля генераторов для открытой таблицы
    def open_table(self, item:QListWidgetItem, alch_table):
        self.clear_generator()
        self.alch_table = alch_table
        self.lw_columns.clear()
        self.lw_columns.addItems([str(col.name) for col in self.alch_table.columns])
        self.dict_of_list_with_values.clear()
        self.dict_of_list_with_values = {str(col.name):[] for col in self.alch_table.columns}



    # Инициализация генераторов для отдельного поля в отношении
    def select_column(self, item:QListWidgetItem):
        self.lbl_datatype.setText(str(self.alch_table.columns[item.text()].type))
        self.selected_datatype = self.alch_table.columns[item.text()].type.python_type
        self.selected_column = item.text()
        if self.alch_table.columns[item.text()].autoincrement == True:
            self.sw_generator.setCurrentIndex(0)
        else:
            self.sw_generator.setCurrentIndex(1)
            self.InitLwGenerators(str(self.selected_datatype))
        

    # Отображение виджета параметров для выбранного генератора
    def show_params(self, item:moded_item):
        for c in reversed(range(self.lo_for_generator.count())):
            widgetToRemove = self.lo_for_generator.itemAt(c).widget()
            self.lo_for_generator.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)
        self.lo_for_generator.addWidget(item.widget)
            
    

    # Получение списка значений из поля ввода
    def get_own_var_from_te(self):

        type_ = self.selected_datatype

        def chek_type(item):
            try:
                type_(item)
            except:
                return False
            return True

        # и отправка этих значений в список для дальнейшего использования
        self.list_of_values_for_col = self.te_values.toPlainText().splitlines()
        self.lbl_own_values_count.setText(str(len(self.list_of_values_for_col)))
        
        if False in list(map(chek_type, self.list_of_values_for_col)):
            self.lbl_datatype_warning.show()
        else:
            self.lbl_datatype_warning.hide()


    def set_generator(self):
        if self.sw_generator.currentIndex() == 0:
            say = QMessageBox.critical(self.main, "", "auto_increment")
        elif self.sw_generator.currentIndex() == 1:
            say = QMessageBox.critical(self.main, "", "")
        elif self.sw_generator.currentIndex() == 2:
            say = QMessageBox.critical(self.main, "", "Сначала установите генератор")
        elif self.sw_generator.currentIndex() == 3:
            say = QMessageBox.critical(self.main, "", "")
        
        # обрабатываем генератор созданный вручную
        elif self.sw_generator.currentIndex() == 4:
            

            if len(self.list_of_values_for_col) == 0:
                say = QMessageBox.critical(self.main, "", "Нет значений")
                return

            if int(self.lbl_own_values_count.text()) < self.sb_cortages.value():
                say = QMessageBox.question(self.main, "", "Вы пытаетесь установить количество кортежей больше чем количество уникальных значений, вы хотите продолжить?")
                if say == QMessageBox.No:
                    return

            # Проверяем установлен ли генератор на столбец        
            try:
                check = read_dbg()[self.main.db_name][self.alch_table.name][self.selected_column] != None
            except KeyError:
                check = False

            if check:
                say = QMessageBox.question(self.main, "", "У вас уже есть установленный генератор на этом столбце, вы хотите продолжить?")
                if say == QMessageBox.No:
                    return


            #Сериализуем генератор для дальнейшего использования
            man_generator = manual(self.list_of_values_for_col)
            set_generator(self.main.db_name, self.alch_table.name, self.selected_column, man_generator)
            
            # устанавливаем пометку зеленым цветом 
            self.lw_columns.item([l.name for l in self.alch_table.columns].index(self.selected_column)).setBackground(QColor(140,255,153))
            
            
    # приведение виджета модуля генераторов к исходному виду
    def clear_generator(self):
        self.lw_generators.clear()
        self.sw_generator.setCurrentIndex(2)

    # привязывается к кнопке ввода собственных значений и отправляет к соответствующему виджету
    def set_own_var(self):
        self.sw_generator.setCurrentIndex(4)
        self.te_values.clear()       

    # привязывается к кнопке ввода значений из другого отношения и отправляет к соответствующему виджету
    def set_other_var(self):
        self.sw_generator.setCurrentIndex(3)

    # привязывается к кнопке возврата к списку генераторов и отправляет к главному виджету
    def get_back(self):
        self.sw_generator.setCurrentIndex(1)



def main():
    # write_dbg({
    #     "mydatabase":{
    #         "книги_редакторы":{
    #             "код_книги":None
    #         }
    #     }
    # })

    #print(read_dbg())

    # man = manual(["df", "df", "df"])

    #set_generator("mydatabase", "книги_редакторы", "код_книги", man)

    write_dbg({})
    
    print(read_dbg())

    
if __name__ == '__main__':
    main()






