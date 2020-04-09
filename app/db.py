from app import app
from flask import g, current_app
import cx_Oracle
import logging
import time

def connect_db(username='dazhi', password='Oracle233', address='oracle.cise.ufl.edu/orcl'):
    """
    Create a connection to the database.
    """
    logger = current_app.logger
    logger.info("Establishing a new connection to the database")
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

def query(sql, limit=None):
    """
    A wrapper for SQL query with logging.
    """
    logger = current_app.logger
    logger.info(f"Query: {sql}")
    db = get_db()
    cur = db.cursor()
    time_start = time.time()
    cur.execute(sql)
    rows = cur.fetchall()
    time_end = time.time()
    logger.info(f'{len(rows)} row(s) fetched in {time_end - time_start:.5f} seconds')
    # Show the first 5 rows for debugging
    for i in range(min(len(rows), 5)):
        logger.debug(f'{rows[i]}')
    return rows

@app.teardown_appcontext
def close_db(error):
    """
    Close db connection at the end of request.
    """
    if hasattr(g, 'oracle_db'):
        logger = current_app.logger
        logger.info("Closing the connection to the database")
        g.oracle_db.close()
