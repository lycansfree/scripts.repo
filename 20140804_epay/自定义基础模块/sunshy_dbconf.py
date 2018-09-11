DBUSER = 'nagios_m'
DBPWD = 'Nagi_!22*'

def OracleConn(sid):
    try:
        import cx_Oracle
        _status = True
        db = cx_Oracle.connect(DBUSER,DBPWD,sid)

    except Exception,e:
        _status = False
        db = -2

    finally:
        return _status,db

