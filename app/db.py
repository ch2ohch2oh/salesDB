from app import app
import cx_Oracle
import logging
from flask import g

def connect_db(username='dazhi', password='Oracle233', address='oracle.cise.ufl.edu/orcl'):
    """
    Create a connection to db.
    """
    con = cx_Oracle.connect(username, password, address, encoding="utf-8")
    return con

def get_db():
    """
    Create a new db connection if there is none for the current
    application context.

    See also:
        https://flask.palletsprojects.com/en/0.12.x/tutorial/dbcon/
    """
    if not hasattr(g, 'oracle_db'):
        g.oracle_db = connect_db()
    return g.oracle_db
    
@app.teardown_appcontext
def close_db(error):
    """
    Close db connection at the end of request.
    """
    if hasattr(g, 'oracle_db'):
        g.oracle_db.close()