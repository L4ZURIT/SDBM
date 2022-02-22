from faker import Faker
import sys
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from sqlalchemy import Table


sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request

class Generator():

    #целочисленные 
    _int = [
        "Одно значение",
        "По порядку с шагом",
        "В обратном порядке с шагом",
        "Случайное число"
    ]

    #дробночисленные 

    _float = [
        "Одно значение",
        "По порядку с шагом",
        "В обратном порядке с шагом",
        "Случайное число"
    ]

    #строковые
    _str = [
        "Адрес", 
        "Телефон", 
        "Электронная почта", 
        "ФИО", 
        "Банковская карточка", 
        "Профессия"
    ]

    #дата

    #время

    #датавремя

    _datetime = [
        "Дата рождения"
    ]

    #логические

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

        print(self.te_values.toPlainText().splitlines())

                
        
        # Связка сигналов
        self.main.lw_tables.itemDoubleClicked.connect(self.open_table)
        self.lw_columns.itemDoubleClicked.connect(self.select_column)
        self.pb_set_vars.clicked.connect(self.set_own_var)


        # 
        self.sw_generator.setCurrentIndex(2)

        
        
        
        pass

    def open_table(self):
        self.alch_table = self.main.tables_manager.alch_table

        self.lw_columns.clear()

        self.lw_columns.addItems([str(col.name) for col in self.alch_table.columns])

        
        pass

    def select_column(self, item:QListWidgetItem):
        self.lbl_datatype.setText(str(self.alch_table.columns[item.text()].type))
        if self.alch_table.columns[item.text()].autoincrement == True:
            self.sw_generator.setCurrentIndex(0)
        else:
            self.sw_generator.setCurrentIndex(1)
            

        pass

    def set_own_var(self):
        self.sw_generator.setCurrentIndex(3)



def main():
    print(Generator._datetime[0])

    pass

if __name__ == '__main__':
    main()





