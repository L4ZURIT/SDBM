DATABASE = {
    'drivername': 'mysql', #Тут можно использовать MySQL или другой драйвер
    'host': 'remotemysql.com',
    'port': '3306',
    'username': 'OKm2FgXiqp',
    'password': 'EOdoJvntQF',
    'database': 'OKm2FgXiqp'
}


from sqlalchemy import *
from sqlalchemy.engine.url import URL

from dateutil import parser


    
def main():
    
    # engine = create_engine(URL.create(**DATABASE))

    # md = MetaData(bind=engine)
    # test = Table("test_2", md, autoload_with=engine)

    # headers = ["id", "var"]
    # row = ["2", "c"]

    # print(test.columns.get("id", "var"))

    # sql = test.delete().where(and_(test.columns.get(headers[i]) == test.columns.get(headers[i]).type.python_type(row[i]) for i in range(len(row))))
    # print(sql.compile(compile_kwargs={"literal_binds": True}))


    print(parser.parse("2000-06-01"))

    
    


if __name__ == "__main__":
    main()