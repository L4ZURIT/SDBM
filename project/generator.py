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
from project.sql import sqlm
from project.request import Request



class serialize():
    # метод для сериализации
    def __getstate__(self):
        return self.__dict__
    
    # метод для десериализации
    def __setstate__(self, d):
        self.__dict__ = d
        self.__init__(**d)
        #self.__init__(self.__dict__["values"])

class Qt:
    class CheckBox(QCheckBox, serialize):
        txt:str = None
        def __init__(self, txt) -> None:
            QCheckBox.__init__(self, txt)
            self.txt = txt

    class Label(QLabel, serialize):
        txt:str = None
        def __init__(self, txt) -> None:
            QLabel.__init__(self, txt)
            self.txt = txt
        
   


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
    

    # Виджет генератора для ФИО 
class FIO(QWidget, serialize):
    def __init__(self, **kwargs) -> None:
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.cb_male = Qt.CheckBox("Мужские")
        self.cb_female = Qt.CheckBox("Женские")
        self.layout().addWidget(self.cb_male)
        self.layout().addWidget(self.cb_female)
        self.layout().setContentsMargins(0,0,0,0)

    def generate_random(self, count:int):
        fake = Faker("ru_RU")
        return [fake.name() for _ in range(count)]

    def generate_unique(self):
        pass   




class borrow(QWidget, serialize):
    table_name:str = None
    column_name:str = None
    
    def __init__(self, fk, sql:sqlm) -> None:
        QWidget.__init__(self)
        self.fk = fk
        self.sql = sql

    def get_all_values(self):
        values = []
        for key in self.fk:
            for val in self.sql.get_column(key.column.table, key.column.name):
                values.append(val)
        return values


    def generate_random(self, count:int) -> list:
        return random.choices(self.get_all_values(), k = count)

    def generate_unique(self, count:int) -> list:
        return random.sample(self.values, count)




# Генератор для значений вводимых вручную
class manual(QWidget, serialize):
    values:list = None
    def __init__(self, values:list) -> None:
        QWidget.__init__(self)
        self.values = values

    def generate_random(self, count:int) -> list:
        return random.choices(self.values, k = count)

    def generate_unique(self, count:int) -> list:
        return random.sample(self.values, count)

class empty(QWidget, serialize):
    def __init__(self, **kwargs):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.lbl = Qt.Label("НЕТ ВИДЖЕТА")
        self.layout().addWidget(self.lbl)
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
            self.widget = empty()

class gb_for_keys(QGroupBox):
    def __init__(self, table_name, column_name):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setTitle("Внешний ключ")
        self.layout().addWidget(QLabel("Таблица:"))
        self.layout().addWidget(QLabel(str(table_name)))
        self.layout().addWidget(QLabel("Столбец:"))
        self.layout().addWidget(QLabel(str(column_name)))
        



# Инициализирующий класс модуля генераторов
class Generator():

    def __init__(self, main:QMainWindow) -> None:
        # Переменные
        self.main:QMainWindow = main
        self.alch_table:Table = None
        self.sql = main.sqlm
        self.lw_columns:QListWidget = main.lw_columns
        self.lw_fk_values:QListWidget = main.lw_fk_values
        self.sw_generator:QStackedWidget = main.sw_generator
        self.gb_parametres:QGroupBox = main.gb_parametres
        self.te_values:QTextEdit = main.te_values
        self.lw_generators:QListWidget = main.lw_generators
        self.lo_for_generator:QLayout = main.lo_for_generator
        self.lo_for_fks:QVBoxLayout = main.lo_for_fks
        self.lbl_own_values_count:QLabel = main.lbl_own_values_count
        self.lbl_datatype_warning:QLabel = main.lbl_datatype_warning
        self.lbl_datatype:QLabel = main.lbl_datatype
        self.lbl_description:QLabel = main.lbl_description
        self.pb_save_generator:QPushButton = main.pb_save_generator
        self.sb_cortages:QSpinBox = main.sb_cortages
        self.tb_find_generator:QToolButton = main.tb_find_generator
        self.tw_preview:QTableWidget = main.tw_preview
        self.selected_column:str = None
        self.selected_datatype:type = None


        # установленные значения для столбца
        self.list_of_values_for_col:list = []
        # установленные наборы значений для таблицы
        self.dict_of_list_with_values:dict = {}


        self.ToolButtonInit()
                
        
        # Связка сигналов
        
        self.lw_columns.itemClicked.connect(self.select_column)
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
            gen = read_dbg()[self.main.db_name][self.alch_table.name][self.selected_column]
            if isinstance(gen, manual):
                self.sw_generator.setCurrentIndex(4)
                cont = "\n".join(gen.values)
                self.te_values.setText(cont)
        except KeyError:
            gen = None
        try:
            for index, item in enumerate(dict_generators[dtype]):
                self.lw_generators.addItem(
                    moded_item(
                        dict_generators[dtype][item]["name"], 
                        dict_generators[dtype][item]["description"], 
                        dict_generators[dtype][item]["var_list"], 
                        dict_generators[dtype][item]["edit"], 
                        dict_generators[dtype][item]["widget"]))
                if dict_generators[dtype][item]["widget"]:
                    if isinstance(gen, eval(dict_generators[dtype][item]["widget"])):
                        self.lw_generators.item(index).setBackground(QColor(140,255,153))
        except KeyError:
            self.lw_generators.addItem(QListWidgetItem("Для выбранного типа данных, не существует генератора"))
            return
        
        
            

    # инициализация модуля генераторов для открытой таблицы
    def open_table(self, item:QListWidgetItem, alch_table):
        self.clear_generator()
        self.alch_table = alch_table
        self.lw_columns.clear()
        self.lw_columns.addItems([str(col.name) for col in self.alch_table.columns])
        self.dict_of_list_with_values.clear()
        self.dict_of_list_with_values = {str(col.name):[] for col in self.alch_table.columns}

        for r in range(self.lw_columns.count()):
            if self.alch_table.columns[self.lw_columns.item(r).text()].autoincrement == True:
                self.lw_columns.item(r).setBackground(QColor(140,255,153))  
            elif self.alch_table.columns[self.lw_columns.item(r).text()].foreign_keys:
                self.lw_columns.item(r).setBackground(QColor(140,255,153))

        gens = read_dbg()
        if gens[self.main.db_name][self.alch_table.name]:
            self.init_generator(gens[self.main.db_name][self.alch_table.name])
            self.init_gen_cont_table(gens[self.main.db_name][self.alch_table.name])
        else:
            self.tw_preview.setColumnCount(0)
            self.tw_preview.setRowCount(0)

    def init_generator(self, generators):
        for col in generators.keys():
            try:
                self.lw_columns.item([l.name for l in self.alch_table.columns].index(col)).setBackground(QColor(140,255,153))
            except ValueError as err:
                reply = QMessageBox.critical(self.main, "", str(err.args))

    def init_gen_cont_table(self, generators):
        self.tw_preview.setRowCount(self.sb_cortages.value())
        self.tw_preview.setColumnCount(len(self.alch_table.columns))
        self.tw_preview.setHorizontalHeaderLabels([str(col.name) for col in self.alch_table.columns])
        
        col_labels = [self.tw_preview.horizontalHeaderItem(col_idx).text() for col_idx in range(self.tw_preview.columnCount())]


        for c_idx, labe in enumerate(col_labels):
            if labe in generators.keys():
                content = generators[labe].generate_random(self.tw_preview.rowCount())
                for r_idx, item in enumerate(content):
                    self.tw_preview.setItem(r_idx, c_idx, QTableWidgetItem(item))
                    self.tw_preview.item(r_idx, c_idx).setBackground(QColor(140,255,153))
            elif self.alch_table.columns[labe].autoincrement == True:
                for row in range(self.tw_preview.rowCount()):
                    self.tw_preview.setItem(row, c_idx, QTableWidgetItem())
                    self.tw_preview.item(row, c_idx).setText("a_i")
                    self.tw_preview.item(row, c_idx).setBackground(QColor(140,255,153))
            elif self.alch_table.columns[labe].foreign_keys:
                b = borrow(self.alch_table.columns[labe].foreign_keys, self.sql)
                vals = b.generate_random(self.tw_preview.rowCount())
                for r_idx, fk_item in enumerate(vals):
                    self.tw_preview.setItem(r_idx, c_idx, QTableWidgetItem(str(fk_item)))
                    self.tw_preview.item(r_idx, c_idx).setBackground(QColor(140,255,153))
            else:
                for row in range(self.tw_preview.rowCount()):
                    self.tw_preview.setItem(row, c_idx, QTableWidgetItem())
                    self.tw_preview.item(row, c_idx).setBackground(QColor(255,107,129))
                

    def InitForeignKeys(self, foreign_keys):
        b = borrow(foreign_keys, self.sql)
        values = b.get_all_values()
        self.lw_fk_values.clear()
        for val in values:
            self.lw_fk_values.addItem(QListWidgetItem(str(val)))
        for c in reversed(range(self.lo_for_fks.count())):
            widgetToRemove = self.lo_for_fks.itemAt(c).widget()
            self.lo_for_fks.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)
        for fk in foreign_keys:
            self.lo_for_fks.addWidget(gb_for_keys(fk.column.table, fk.column.name))
        




    # Инициализация генераторов для отдельного поля в отношении
    def select_column(self, item:QListWidgetItem):
        self.lbl_datatype.setText(str(self.alch_table.columns[item.text()].type))
        self.selected_datatype = self.alch_table.columns[item.text()].type.python_type
        self.selected_column = item.text()
        if self.alch_table.columns[item.text()].autoincrement == True:
            self.sw_generator.setCurrentIndex(0)
        elif self.alch_table.columns[item.text()].foreign_keys:
            self.sw_generator.setCurrentIndex(3)
            self.InitForeignKeys(self.alch_table.columns[item.text()].foreign_keys)
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
        self.lbl_description.setText(item.description)
            
    

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

        # Проверяем установлен ли генератор на столбец        
        try:
            check = read_dbg()[self.main.db_name][self.alch_table.name][self.selected_column] != None
        except KeyError:
            check = False

        if check:
            say = QMessageBox.question(self.main, "", "У вас уже есть установленный генератор на этом столбце, вы хотите продолжить?")
            if say == QMessageBox.No:
                return


        if self.sw_generator.currentIndex() == 0:
            say = QMessageBox.critical(self.main, "", "auto_increment")

        # обрабатываем генератор выбранный из меню
        elif self.sw_generator.currentIndex() == 1:

            #Сериализуем генератор для дальнейшего использования
            try:
                gnrtr = self.lw_generators.selectedItems()[0].widget
            except IndexError:
                reply = QMessageBox.critical(self.main, "", "Связать что?")
                return
            if isinstance(gnrtr, empty):
                reply = QMessageBox.critical(self.main, "", "У генератора нет генератора")
                return
            set_generator(self.main.db_name, self.alch_table.name, self.selected_column, gnrtr)

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

            #Сериализуем генератор для дальнейшего использования
            man_generator = manual(self.list_of_values_for_col)
            set_generator(self.main.db_name, self.alch_table.name, self.selected_column, man_generator)
            
        # устанавливаем пометку зеленым цветом 
        self.lw_columns.item([l.name for l in self.alch_table.columns].index(self.selected_column)).setBackground(QColor(140,255,153))
        self.init_gen_cont_table(read_dbg()[self.main.db_name][self.alch_table.name])
            
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
        notice = QMessageBox.information(self.main, "Установка значений из другого столбца", "Данный модуль поможет вам сгенерировать значения на основе параметров внешнего ключа. Чтобы этот модуль работал достаточно лишь установить соответствующие ограничения в вашей базе и приложение распознает его автоматически")

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

    # obj:QWidget = read_dbg()["mydatabase"]["книги_редакторы"]["код_редактора"]
    # print(obj.windowTitle())

   







    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
    


