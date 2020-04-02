from app.db import connect_db
import cx_Oracle

def test_db_standalone():
    # print("LOGIN CREDENTIALS".center(40, '='))
    username = 'dazhi'
    # print(f"Username: {username}")
    # password = input('Password: ')
    password = 'Oracle233'
    con = cx_Oracle.connect(username, password, 'oracle.cise.ufl.edu/orcl', encoding = 'UTF-8')
    cursor = con.cursor()
    rows = list(cursor.execute('select * from city'))
    assert len(rows) == 96
    con.commit()
    con.close()

def test_connect_db():
    con = connect_db()
    cur = con.cursor()
    assert len(list(cur.execute('select * from city'))) == 96