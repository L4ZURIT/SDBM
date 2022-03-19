import itertools
import json
import sys
import pymysql
import pandas as pd
import numpy as np

from datetime import date, datetime, time, timedelta

from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.exc import ResourceClosedError

from sqlalchemy.dialects import mysql


# взято с сайта https://question-it.com/questions/1490148/sqlalchemy-vyvesti-fakticheskij-zapros
# специальный метод конструктора выражений правильно работающий с датой и временем (НАДО ГРАМОТНО ОФОРМИТЬ)
def render_query(statement, dialect=None):
    """
    Generate an SQL expression string with bound parameters rendered inline
    for the given SQLAlchemy statement.
    WARNING: This method of escaping is insecure, incomplete, and for debugging
    purposes only. Executing SQL statements with inline-rendered user values is
    extremely insecure.
    Based on http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query
    """
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
            if isinstance(value, int):
                return str(value)
            elif isinstance(value, (str, date, datetime, timedelta)):
                return "'%s'" % str(value).replace("'", "''")
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
        try:
            tab = pd.read_sql(str(req.compile(self.engine)), conn)
            ans = tab.to_dict(orient='list')
            return ans
        except Exception as e:
            print(e)
            return e



if __name__ == "__main__":
    s = sqlm()
    alch = Table("книги", s.md, autoload_with=s.engine)

    req = alch.select()
    print(req)
    print(s.request(req))

    req = alch.insert().values(**{
        "номер_книги": len(str(s.request(req)).splitlines())+1,
        "название_книги": "7",
        "дата_выхода":datetime(2000, 12,12,12,12),
        "тираж":100,
        "ответственный_редактор":"go"

    })


    print(req.compile(compile_kwargs={"literal_binds": True}))
    print(s.request(req))


    
    
     