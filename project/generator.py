from faker import Faker
import sys
import json
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from sqlalchemy import Table


sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request
from test import human

class gogo():
    def __init__(self) -> None:
        print("ya puknul")
        pass

parametres = {
    "a":gogo}

class moded_item(QListWidgetItem):
    def __init__(self, name, description, var_list, edit, widget) -> None:
        super().__init__()
        self.setText(name)
        self.description = description
        self.var_list = var_list
        self.edit = edit
        try:
            self.widget = parametres[widget]()
        except KeyError:
            print("У генератора '%s' не настроен виджет параметров"%name)


class Generator():

    def __init__(self, main:QMainWindow) -> None:
        # Переменные
        self.main:QMainWindow = main
        self.alch_table:Table = None
        self.lw_columns:QListWidget = main.lw_columns
        self.lbl_datatype:QLabel = main.lbl_datatype
        self.sw_generator:QStackedWidget = main.sw_generator
        self.gb_parametres:QGroupBox = main.gb_parametres
        self.pb_set_vars:QPushButton = main.pb_set_vars
        self.te_values:QTextEdit = main.te_values
        self.pb_set_other:QPushButton = main.pb_set_other
        self.lw_generators:QListWidget = main.lw_generators
        self.lo_for_generator:QLayout = main.lo_for_generator
        self.pb_back_1:QPushButton = main.pb_back_1
        self.pb_back_2:QPushButton = main.pb_back_2


                
        
        # Связка сигналов
        self.main.lw_tables.itemDoubleClicked.connect(self.open_table)
        self.lw_columns.itemDoubleClicked.connect(self.select_column)
        self.pb_set_vars.clicked.connect(self.set_own_var)
        self.pb_set_other.clicked.connect(self.set_other_var)
        self.pb_back_1.clicked.connect(self.get_back)
        self.pb_back_2.clicked.connect(self.get_back)


        # 
        self.sw_generator.setCurrentIndex(2)

        
    
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
            

    def open_table(self):
        self.clear_generator()
        self.alch_table = self.main.tables_manager.alch_table
        self.lw_columns.clear()
        self.lw_columns.addItems([str(col.name) for col in self.alch_table.columns])


    def select_column(self, item:QListWidgetItem):
        self.lbl_datatype.setText(str(self.alch_table.columns[item.text()].type))
        selected_datatype = str(self.alch_table.columns[item.text()].type.python_type)
        if self.alch_table.columns[item.text()].autoincrement == True:
            self.sw_generator.setCurrentIndex(0)
        else:
            self.sw_generator.setCurrentIndex(1)
            self.InitLwGenerators(selected_datatype)
            

    def clear_generator(self):
        self.lw_generators.clear()
        self.sw_generator.setCurrentIndex(2)

    def set_own_var(self):
        self.sw_generator.setCurrentIndex(4)

    def set_other_var(self):
        self.sw_generator.setCurrentIndex(3)

    def get_back(self):
        self.sw_generator.setCurrentIndex(1)



def main():
    

    pass

if __name__ == '__main__':
    main()





