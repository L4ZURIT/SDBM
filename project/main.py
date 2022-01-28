from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys





sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request
from project.tables import Tables


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
        # ----

        # настройка интерфейса 

        
        # ---





        # self.split = QSplitter()
        # self.split.addWidget(QListWidget())
        # self.split.addWidget(QTextEdit())

        # self.lo_for_split.addWidget(self.split)



        

    
        


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
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())