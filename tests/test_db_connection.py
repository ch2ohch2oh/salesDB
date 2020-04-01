import cx_Oracle

def test_db_connection():
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