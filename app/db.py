import cx_Oracle
import logging

class DatabaseConnection:
    logger = logging.getLogger('DatabaseConnection')

    def __init__(self, username='dazhi', password='Oracle233', address='oracle.cise.ufl.edu/orcl'):
        self.conn = cx_Oracle.connect(username, password, address, encoding="utf-8")
        logger.info('Database connection established.')

    def execute(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)

    def fetchall(self, sql):
        rows = None
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.conn.commit()
        return rows
    
    def __del__(self):
        if self.conn:
            self.conn.close()

if __name__ == '__main__':
    db = DatabaseConnection()
