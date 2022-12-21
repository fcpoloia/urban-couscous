#!/usr/bin/env python3


#
# tables - config, photos, videos, models, sites
#
# select * from config;
# pragma table_info(config);
#

"""
"""


import sqlite3
import sys
import re
import os
import glob

class DatabaseMissingError(Exception):
    pass

class BasicDB:
    def __init__(self):
        self.conn = None

    def connectdb(self, database):
        if os.path.exists(database):
            self.conn = sqlite3.connect(database)
        else:
            raise DatabaseMissingError

    def closedb(self):
        self.conn.close()

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def execute(self, sql):
        self.conn.execute(sql)

    def num_cols(self, table):
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


#------------------------------------------------------------------------------
# select(cols).from(table).where(clause).group_by(col).order_by(col).desc()
# select().star().from(table).where(clause).group_by(col).order_by(col).asc()
#
class Query:
    def __init__(self):
        self.sql = ""

    def select(self, cols):
        self.sql += f"select {cols}"
        return self
        
    def _from(self, table):
        self.sql += f" from {table}"
        return self
        
    def where(self, clause):
        self.sql += f" where {clause}"
        return self

    def group_by(self, col):
        self.sql += f" group by {col}"
        return self

    def order_by(self, col):
        self.sql += f" order by {col}"
        return self
        
    def desc(self):
        self.sql += f" desc"
        return self

    def asc(self):
        self.sql += f" asc"
        return self

    def __call__(self):
        return self.sql
        
#------------------------------------------------------------------------------
class Table(BasicDB):
    def __init__(self, dbname, tblname):
        self.name = tblname
        self.sql_all = f"SELECT * FROM {self.name} "
        self.pragma = f"pragma table_info({self.name});"
        self.connectdb(dbname)
        #self.distinct = ''
        
    def col_count(self):
        return len(self.get_results_list(self.pragma, 6))
    
    def row_count(self):
        sql = f"SELECT COUNT() FROM {self.name};"
        return self.get_single_result(sql, 1)[0]

    def column_list(self):
        res = self.get_results_list(self.pragma, 2)
        columns = []
        for col in res:
            columns.append(col[1])
        return columns
        
    #def set_distinct(self):
    #    self.distinct = 'DISTINCT'
    #    return self


    def select_all(self):
        return self.get_results_list(self.sql_all, self.col_count())
        
    def select_where(self, column, value):
        sql = self.sql_all + f"where {column} = '{value}' "
        return self.get_results_list(sql, self.col_count())
        
    def select_order_by(self, order_col, direction):
        sql = self.sql_all + f"order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())
        
    def select_group_by_order_by(self, group_col, order_col, direction):
        sql = self.sql_all + f" group by {group_col} order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())
        
    def select_where_order_by(self, column, value, order_col, direction):
        sql = self.sql_all + f"where {column} = '{value}' order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())
        
    def select_where_group_by_order_by(self, column, value, group_col, order_col, direction):
        sql = self.sql_all + f"where {column} = '{value}' group by {group_col} order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())
        
    def select_by_most_recent_photos(self, col, order='desc'): 
        """this will only actually work for models table which has thumb column"""
        sql = f"select {self.name}.id,{self.name}.name,{self.name}.thumb from {self.name} join photos on {self.name}.id=photos.{col} group by photos.{col} order by photos.id {order};"
        return self.get_results_list(sql, self.col_count()+1)

    def select_by_most_recent_videos(self, col, order='desc'): 
        """this will only actually work for models table which has thumb column"""
        sql = f"select {self.name}.id,{self.name}.name,{self.name}.thumb from {self.name} join videos on {self.name}.id=videos.{col} group by videos.{col} order by videos.id {order};"
        return self.get_results_list(sql, self.col_count()+1)

    def nn():
        """"""
        sql="select count(models.id),models.id,models.name,photos.model_id,videos.model_id from models join photos on photos.model_id=models.id join videos on videos.model_id=models.id group by models.id order by count(models.id) desc;"

    def get_next_prev(self, id, col=None, val=None):
        """"""
        query = ""
        if col is not None and val is not None:
            query = f"{col}='{val}' and "
        
        sql = f"SELECT id FROM {self.name} WHERE {query} id %s {id} ORDER BY id %s LIMIT 1;"
        pid = self.get_single_result(sql % ('<','desc'), 1)[0]
        nid = self.get_single_result(sql % ('>','asc'), 1)[0]
        pn = nn = ''
        if pid is not None: pn = self.get_single_result(f"select name from {self.name} where id = {pid}", 1)[0]
        if nid is not None: nn = self.get_single_result(f"select name from {self.name} where id = {nid}", 1)[0]
        return nid, pid, nn, pn

    def select_where_like(self, column, value):
        sql = self.sql_all + f"where {column} like '%{value}%'" # group by id order by id desc"
        return self.get_results_list(sql, self.col_count())

    def select_where_like_group_order(self, column, value, group, order, direction):
        sql = self.sql_all + f"where {column} like '%{value}%' group by {group} order by {order} COLLATE NOCASE {direction}"
        return self.get_results_list(sql, self.col_count())


# get a list of model names ordered by set count

#------------------------------------------------------------------------------
class ModelsTable(Table):
    def __init__(self, dbname):
        super().__init__(dbname, 'models')

    def select_models_by_count(self, order):
        """list models by largest count of combined photosets and videos"""
        sql = f"select models.id,models.name,models.thumb from models join photos on photos.model_id=models.id join videos on videos.model_id=models.id group by models.id order by count(models.id) {order};"
        sql = f"select models.id,models.name,models.thumb,count(models.id) from models left join photos on photos.model_id=models.id group by models.id  union all select models.id,models.name,models.thumb,count(models.id)  from models left join videos on videos.model_id=models.id where models.id is null group by models.id order by count(models.id) {order} ;"
        return self.get_results_list(sql, self.col_count())

class SitesTable(Table):
    def __init__(self, dbname):
        super().__init__(dbname, 'sites')

    def select_sites_by_count(self, order):
        """list sites by largest count of combined photosets and videos"""

        sql = f"select sites.id,sites.name,sites.location,count(sites.id) from sites left join photos on photos.site_id=sites.id group by sites.id  union all select sites.id,sites.name,sites.location,count(sites.id)  from sites left join videos on videos.site_id=sites.id where sites.id is null group by sites.id order by count(sites.id) {order} ;"
        result = self.get_results_list(sql, self.col_count())
        print(f"{len(result)} {result}")
        return result

class PhotosTable(Table):
    def __init__(self, dbname):
        super().__init__(dbname, 'photos')

class VideosTable(Table):
    def __init__(self, dbname):
        super().__init__(dbname, 'videos')

class ConfigTable(Table):
    def __init__(self, dbname):
        super().__init__(dbname, 'config')



#------------------------------------------------------------------------------

# we need an insert query to add photo set or video that can establish site_id and model_id

#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    DATABASE = "new_kindgirls.db"
    
    p = PhotosTable(DATABASE)
    print(len( p.select_all()))
    print(len( p.select_where('model_id',3)))
    print(len( p.select_where('site_id',3)))
    print(p.get_next_prev(10437))
    
    v = VideosTable(DATABASE)
    print(len( v.select_all()))
    print(len( v.select_where('model_id',7)))
    print(len( v.select_where('site_id',2)))
    print(len( v.select_order_by('length', 'desc')))
    print(len( v.select_where_order_by('model_id', 7, 'length', 'asc')))
    print(v.get_next_prev(360))

    c = ConfigTable(DATABASE)
    print(c.select_all())
    print(c.column_list())
    
    print(len(p.select_where_like('name','mango')))
    #print(len(p.select_where_like('name','mango')))
    
    q = Query()
    b = BasicDB()
    b.connectdb(DATABASE)
    sql = q.select('*')._from('photos').where("name like '%mango%'")()
    res = b.get_results_list(sql, b.num_cols('photos'))
    print(len(res))
    for row in res:
        print(row)
    
    s = SitesTable(DATABASE)
    print("select sites by count")
    print(s.select_sites_by_count('desc'))

