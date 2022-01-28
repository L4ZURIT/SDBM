from datetime import datetime
import json
from re import M
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import pymysql

sys.path.insert(1, './')
from project.mysql import mysql_m


class Tables():
    def __init__(self, main:QMainWindow) -> None:

        # Инициализация переменных
        self.st = main.standart
        self.lw_tables:QListWidget = main.lw_tables
        self.tw_content:QTableWidget = main.tw_content
        self.sb_rows:QSpinBox = main.sb_rows
        self.sql:mysql_m = main.sql
        # ---
        
        # Настройка интерфейса
        self.TablesListInit()

        # ---


        # Связка сигналов
        self.lw_tables.itemDoubleClicked.connect(self.open_table)

        # ---

        # Переопределение событий

        # ---
        

    def TablesListInit(self):
        tables = self.sql.request(self.sql.get_tables())
        for table in tables:
            self.lw_tables.addItem(str(table[0]))

    def open_table(self, item:QListWidgetItem):



        self.sql.SetSend(True)

        self.tw_content.clear()

        data = self.sql.get_table(item.text())
        keys = list(data.keys())
        values = list(data.values())
        self.tw_content.setRowCount(self.sb_rows.value())
        self.tw_content.setColumnCount(len(keys))

        self.tw_content.setIndexWidget()

        for col in range(len(keys)):
            self.tw_content.setHorizontalHeaderItem(col, QTableWidgetItem(str(keys[col])))
            for row in range(len(values[col])):
                self.tw_content.setItem(row, col, QTableWidgetItem(str(values[col][row])))

        self.sql.SetSend(self.st)

