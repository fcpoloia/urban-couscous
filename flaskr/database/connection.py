
import os
import sqlite3

from flaskr.database.errors import DatabaseMissingError


class ConnectDB:
    """"""
    def __init__(self):
        """"""
        self.conn = None

    def connectdb(self, database):
        """"""
        if os.path.exists(database):
            self.conn = sqlite3.connect(database)
        else:
            raise DatabaseMissingError

    def closedb(self):
        """"""
        self.conn.close()

    def cursor(self):
        """"""
        return self.conn.cursor()

    def commit(self):
        """"""
        self.conn.commit()

    def execute(self, sql):
        """"""
        self.conn.execute(sql)

    def num_cols(self, table):
        """"""
        return len(self.get_results_list(f"pragma table_info({table});", 6))

    def get_single_result(self, sql, cols):
        """"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            result = [ None for x in range(cols) ]
            for row in cursor:
                result = row[:cols]
            return result
        except sqlite3.OperationalError:
            print(sql)
            raise

    def get_results_list(self, sql, cols):
        """return the result of the sql statement"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            results = []
            for row in cursor:
                results.append(row[:cols])
            return results
        except sqlite3.OperationalError:
            print(sql)
            raise


