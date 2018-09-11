# coding:utf-8

from mysql import connector
from jenkins import Jenkins
import sys,os
import xlrd


def set_dbinfo(insertList):
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '172.16.104.1'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.executemany("insert into jenkins values (%s,%s)",insertList)
        db.commit()
        cur.close()
        db.close()

    except Exception,e:
        print str(e)
        sys.exit(2)

def main():
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    filename = os.path.join(basedir,'ssorder.xlsx')
    insertList = []
    s = xlrd.open_workbook(filename)
    t = s.sheets()[0]
    for i in range(t.nrows):
        insertList.append((t.row(i)[0].value,t.row(i)[1].value))

    set_dbinfo(insertList)


if __name__ == '__main__':
    main()



