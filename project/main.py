from asyncore import write
from datetime import datetime
import json
import logging
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

from pymysql import OperationalError


sys.path.insert(1, './')
from project.mysql import mysql_m



class Request():

    @staticmethod
    def read() -> dict:
        with open("data/requests.json") as json_file:
            data = json.load(json_file)
        return data
        
    @staticmethod
    def write(data):
        with open("data/requests.json", 'w') as f:
            json.dump(data, f)



    def __init__(self, main: QMainWindow):

        # определение переменных
        self.le_req:QLineEdit = main.le_req 
        self.pb_req:QPushButton = main.pb_req
        self.tw_story:QTableWidget = main.tw_story
        self.te_result:QTextEdit = main.te_result
        self.sql:mysql_m = main.sql


        # настройка интерфейса
        self.write_ui(self.read())


        # связка сигналов
        self.pb_req.clicked.connect(self.go)

        # переопределение событий
        self.tw_story.resizeEvent = self.resize_columns

    
    def resize_columns(self, e):
        self.tw_story.setColumnWidth(0, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)
        self.tw_story.setColumnWidth(1, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)
        self.tw_story.setColumnWidth(2, (self.tw_story.width()-20) / self.tw_story.columnCount()*2.5)
        self.tw_story.setColumnWidth(3, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)


    def write_ui(self, diction:dict):
        self.tw_story.clearContents()
        count = len(diction["dates"])
        self.tw_story.setRowCount(count)
        for row in range(count):
            self.tw_story.setItem(row, 0, QTableWidgetItem(diction["dates"][row][:10]))
            self.tw_story.setItem(row, 1, QTableWidgetItem(diction["dates"][row][10:19]))
            self.tw_story.setItem(row, 2, QTableWidgetItem(diction["requests"][row]))
            self.tw_story.setItem(row, 3, QTableWidgetItem(diction["status"][row]))
        

    def write_json(self, content):

        diction = self.read()

        diction["dates"].append(str(datetime.now()))
        diction["requests"].append(self.le_req.text())
        diction["answers"].append(str(content))
        if type(content) == OperationalError:
            diction["status"].append("Fail")
        else: 
            diction["status"].append("OK")

        self.write(diction)
        self.write_ui(diction)


    def clear_json(self):
        req = {
            "dates":[], 
            "requests": [],
            "answers": [],
            "status":[]
        }
        self.write(req)

    

    def go(self):
        self.te_result.clear()
        result = self.sql.request(self.le_req.text())
        self.te_result.setText(str(result))
        self.write_json(result)
        



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('interface/main.ui',self)

        # статус бар начало 
        self.statusBar().addWidget(QLabel("built_version_24.01.2022"))
        self.progress = QProgressBar()
        self.status = QLabel("none")
        self.statusBar().addWidget(self.progress)
        self.statusBar().addWidget(self.status)
        self.progress.hide()
        self.status.hide()
        # статус бар конец

        # инициализация классов начало
        self.sql = mysql_m()
        self.req = Request(self)
        # инициализация классов конец



        

    
        


    #     self.menu = QMenu()
    #     for i in range(5):
    #       self.menu.addAction(str(i))

    #     self.actions_table.setPopupMode(QToolButton.InstantPopup)
    #     self.actions_table.setMenu(self.menu)

        

    # def cont(self, e):
    #     context = QMenu(self)
    #     context.addAction(QAction("test 1", self))
    #     context.addAction(QAction("test 2", self))
    #     context.addAction(QAction("test 3", self))
    #     context.exec(e.globalPos())
        

        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())