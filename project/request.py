from datetime import datetime
import json
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import pymysql


sys.path.insert(1, './')
from project.mysql import mysql_m


class Request():

    m_pb_up = "🠹"
    m_pb_down = "🠻"

    @staticmethod
    def j_read() -> dict:
        with open("data/requests.json") as json_file:
            data = json.load(json_file)
        return data
        
    @staticmethod
    def j_write(data):
        with open("data/requests.json", 'w') as f:
            json.dump(data, f)



    def __init__(self, main: QMainWindow):

        # определение переменных
        self.le_req:QLineEdit = main.le_req 
        self.pb_req:QPushButton = main.pb_req
        self.tw_story:QTableWidget = main.tw_story
        self.te_result:QTextEdit = main.te_result
        self.pb_up_down:QPushButton = main.pb_up_down
        self.te_req:QTextEdit = main.te_req
        self.sql:mysql_m = main.sql


        # настройка интерфейса 
        self.write_ui(self.j_read())
        self.tw_story.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tw_story.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.te_req.hide()
        self.pb_up_down.setText(self.m_pb_up)


        # связка сигналов
        self.pb_req.clicked.connect(self.create_req)
        self.pb_up_down.clicked.connect(self.change_req_widget)
        self.tw_story.cellDoubleClicked[int, int].connect(self.get_from_story)

        # переопределение событий
        self.tw_story.resizeEvent = self.resize_columns

    
    # Растягивает табличку истории запросов в нижнем групбоксе SQL
    def resize_columns(self, e):
        self.tw_story.setColumnWidth(0, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)
        self.tw_story.setColumnWidth(1, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)
        self.tw_story.setColumnWidth(2, (self.tw_story.width()-20) / self.tw_story.columnCount()*2.5)
        self.tw_story.setColumnWidth(3, (self.tw_story.width()-20) / self.tw_story.columnCount()*0.5)



    # Обновляет содержимое таблички истории запросов в нижнем групбоксе SQL
    def write_ui(self, diction:dict):
        self.tw_story.clearContents()
        count = len(diction["dates"])
        self.tw_story.setRowCount(count)
        for row in range(count):
            self.tw_story.setItem(row, 0, QTableWidgetItem(diction["dates"][row][:10]))
            self.tw_story.setItem(row, 1, QTableWidgetItem(diction["dates"][row][10:19]))
            self.tw_story.setItem(row, 2, QTableWidgetItem(diction["requests"][row]))
            self.tw_story.setItem(row, 3, QTableWidgetItem(diction["status"][row]))
        


    # добавляет новые записи в историю запросов находящуюся в файле json
    def write_json(self, content, req):

        diction = self.j_read()

        diction["dates"].append(str(datetime.now()))
        diction["requests"].append(req)
        diction["answers"].append(str(content))
        if  (type(content) == pymysql.err.ProgrammingError or
        type(content) == pymysql.err.DataError or
        type(content) == pymysql.err.IntegrityError or
        type(content) == pymysql.err.NotSupportedError or
        type(content) == pymysql.err.OperationalError):
            diction["status"].append("Fail")
        else: 
            diction["status"].append("OK")

        self.j_write(diction)
        self.write_ui(diction)


    # Полностью очищает json файл
    def clear_json(self):
        req = {
            "dates":[], 
            "requests": [],
            "answers": [],
            "status":[]
        }
        self.j_write(req)
        self.write_ui(req)


    # переключает виджет запросов с полоски на область и обратно
    def change_req_widget(self):
        if self.pb_up_down.text() == self.m_pb_up:
            self.pb_up_down.setText(self.m_pb_down)
            self.te_req.setText(self.le_req.text())
            self.te_req.show()
            self.le_req.hide()
        else:
            self.pb_up_down.setText(self.m_pb_up)
            self.le_req.setText(self.te_req.toPlainText())
            self.le_req.show()
            self.te_req.hide()


    # Передает запрос из активного контейнера запросов в метод осуществления запроса 
    def create_req(self):
        if self.pb_up_down.text() == self.m_pb_up:
            self.go(self.le_req.text())
        else:
            self.go(self.te_req.toPlainText())


    # Метод реализующий запрос к бд, с записью данного запроса в историю и обновляющего информацию в виджетах ручных запросов
    # Таким образом даже автоматические запросы реализуются через даннный метод, чтобы можно было вести их учет и посмотреть подробности в окне ручных запросов
    def go(self, req):
        self.te_result.clear()
        result = self.sql.request(req)
        self.te_result.setText(str(result))
        self.write_json(result, req)
        return result


    # устанавливает данные запроса из истории (состав запроса в его поле и ответ в поле ответа соответствено)
    def get_from_story(self, row, col):
        diction = Request.j_read()
        self.le_req.setText(diction["requests"][row])
        self.te_result.setText(diction["answers"][row])        

