import itertools
import json
import sys
import pymysql
import pandas as pd
import numpy as np

from datetime import date, datetime, time, timedelta
from pymysql import NULL

from sqlalchemy import create_engine, Column, Table, MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Query, scoped_session
from sqlalchemy.exc import ResourceClosedError


# метод построения запроса с параметрами
def render_query(statement, dialect=None):

    if isinstance(statement, Query):
        if dialect is None:
            dialect = statement.session.bind.dialect
        statement = statement.statement
    elif dialect is None:
        dialect = statement.bind.dialect

    class LiteralCompiler(dialect.statement_compiler):

        def visit_bindparam(self, bindparam, within_columns_clause=False,
                            literal_binds=False, **kwargs):
            return self.render_literal_value(bindparam.value, bindparam.type)

        def render_array_value(self, val, item_type):
            if isinstance(val, list):
                return "{%s}" % ",".join([self.render_array_value(x, item_type) for x in val])
            return self.render_literal_value(val, item_type)

        def render_literal_value(self, value, type_):
            # Здесь вписывать необрабатываемые типы данных
            if isinstance(value, int):
                return str(value)
            elif isinstance(value, (str, date, datetime, timedelta, time)):
                return "'%s'" % str(value).replace("'", "''")
            elif value == None:
                return "NULL"
            elif isinstance(value, list):
                return "'{%s}'" % (",".join([self.render_array_value(x, type_.item_type) for x in value]))
            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return LiteralCompiler(dialect, statement).process(statement)




sys.path.insert(1, './')

class sqlm():
    @staticmethod
    def j_read() -> dict:
        with open("data/database.json") as json_file:
            data = json.load(json_file)
        return data

    def __init__(self) -> None:
        self.engine = create_engine(URL.create(**self.j_read()))
        self.md = MetaData(bind=self.engine)
        self.dialect = None
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine))



    def request(self, req):
        conn = self.engine.connect()
        try:
            result = conn.execute(req)
        except Exception as ex:
            return ex
        try:
            return "\n".join([str(res) for res in result])
        except ResourceClosedError:
            return "no_data"

    def get_table(self, table:Table):
        req = table.select()
        conn = self.engine.connect()
        
        #tab = pd.read_sql(str(req.compile(self.engine)), conn)
        res = conn.execute(req)
        tab = pd.DataFrame(res.fetchall())
        ans = tab.to_dict(orient='list')
        if ans == {}:
            ans = {str(col.name):[] for col in table.columns}
        return ans
        






if __name__ == "__main__":
    s = sqlm()
    alch_table = Table("кабинет", s.md, autoload_with=s.engine)

    

    col:Column = alch_table.columns[0]

    print(col.description())


    
    
    
     