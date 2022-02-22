from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys





sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request
from project.tables import Tables
from project.indexes import Indexes
from project.generator import Generator


class MainWindow(QMainWindow):

    standart = False

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('interface/main.ui',self)

        # статус бар  
        self.statusBar().addWidget(QLabel("built_version_24.01.2022"))
        self.progress = QProgressBar()
        self.status = QLabel("none")
        self.statusBar().addWidget(self.progress)
        self.statusBar().addWidget(self.status)
        self.progress.hide()
        self.status.hide()
        # ---

        # инициализация классов 
        self.sql = mysql_m(self.standart)
        self.req = Request(self)
        self.tables_manager = Tables(self)
        self.index_manager = Indexes(self)
        self.generator_manager = Generator(self)
        # ----

        # настройка интерфейса 

        
        # ---

        # связка сигналов  
        self.act_to_main.triggered.connect(self.to_main)
        self.act_to_sql.triggered.connect(self.to_sql)
        
        # ---

    def to_main(self):
        self.stack.setCurrentIndex(1)

    def to_sql(self):
        self.stack.setCurrentIndex(2)
        

        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())