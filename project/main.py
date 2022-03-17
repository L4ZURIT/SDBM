from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys


from sqlalchemy import *
import sqlalchemy
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Query


sys.path.insert(1, './')
from project.mysql import mysql_m
from project.request import Request
from project.tables import Tables
from project.indexes import Indexes
from project.generator import Generator, read_dbg, write_dbg


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
        # - - -

        # инициализация классов 
        self.sql = mysql_m(self.standart)
        self.req = Request(self)
        self.tables_manager = Tables(self)
        self.index_manager = Indexes(self)
        self.generator_manager = Generator(self)
        # ----

        # Инициализация SQLAlchemy
        self.engine = create_engine(URL.create(**mysql_m.j_read()))
        self.md = MetaData(bind=self.engine)
        # ---

        # настройка интерфейса 
        #WARNING!!!!!
        self.gb_SQL.hide()
        #WARNING!!!!!   
        # ---

        # переменные
        self.db_name = "mydatabase"
        # ---

        # Проверяем привязана ли данная база к какому нибудь из генераторов
        self.check_generators()

        # связка сигналов  
        self.act_to_main.triggered.connect(self.to_main)
        self.act_to_sql.triggered.connect(self.to_sql)
        self.lw_tables.itemDoubleClicked.connect(self.init_alch_table)
        # ---

    

    def init_alch_table(self, item:QListWidgetItem):
        self.md = MetaData(bind=self.engine)
        self.alch_table = Table(item.text(), self.md, autoload_with=self.engine)
        self.tables_manager.open_table(item, self.alch_table)
        self.index_manager.open_table(item, self.alch_table)
        self.generator_manager.open_table(item, self.alch_table)

    
    def check_generators(self):
        try:
            read_dbg()[self.db_name]
        except KeyError:
            write_dbg({
                self.db_name:{
                    table:{} for table in sqlalchemy.inspect(self.engine).get_table_names()
                }
            })
            print(read_dbg())
        pass
        

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
