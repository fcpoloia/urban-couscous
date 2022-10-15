#!/usr/bin/env python3

#
# this is used by flaskr/__init__.py in ~/Pictures/kindgirls/
# and by ~/bin/Girls_Site_Rippers/getkindgirls.py
#

# tables - config, kindgirls (photos), videos
#
# select * from config;
# pragma table_info(config);
"""
sqlite> pragma table_info(config);
cid|name|type|notnull|dflt_value|pk
0|id|INT|1||1
1|rootpath|CHAR(256)|0||0
2|title|CHAR(256)|0||0
3|images|CHAR(256)|0||0
4|thumbs|CHAR(256)|0||0
5|videos|CHAR(256)|0||0

sqlite> pragma table_info(kindgirls);
cid|name|type|notnull|dflt_value|pk
0|id|INT|1||1
1|name|CHAR(256)|1||0
2|location|CHAR(256)|1||0
3|site|CHAR(50)|1||0
4|model|CHAR(50)|1||0
5|count|INT|0||0

sqlite> pragma table_info(videos);
cid|name|type|notnull|dflt_value|pk
0|id|INT|1||1
1|name|CHAR(256)|0||0
2|location|CHAR(256)|0||0
3|thumb|CHAR(256)|0||0
4|width|INT|0||0
5|height|INT|0||0
6|length|DOUBLE|0||0
7|model|CHAR(50)|0||0
8|site|CHAR(50)|0||0
"""
#
#

"""
next update to database to add capability for multiple models associated with a phpto set
"""

DATABASE = "/Users/judge/Pictures/kindgirls/kindgirls.db"
DATABASE = "../kindgirls.db"

import sqlite3
import sys
import re
import glob


class BasicDB:

    def __init__(self):
        self.conn = None

    def connectdb(self, database=DATABASE):
        self.conn = sqlite3.connect(database)

    def closedb(self):
        self.conn.close()

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def execute(self, sql):
        self.conn.execute(sql)


#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class GirlsDB(BasicDB):
    def __init__(self):
        pass

    def get_results_list(self, sql, cols):
        """return the result of the sql statement"""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        results = []
        for row in cursor:
            results.append(row[:cols])
        return results

    def get_sites(self):
        """get a list of site names"""
        sql = "SELECT max(id),site,name,location FROM photos GROUP BY site ORDER BY id desc;"
        return self.get_results_list(sql, 4)

    def get_models(self):
        """get a list of model names"""
        sql = "SELECT max(id),model,name,location FROM photos GROUP BY model ORDER BY id desc;"
        return self.get_results_list(sql, 4)

    def get_models_sort_by_set_count(self):
        """get a list of model names"""
        sql = "WITH models as (SELECT max(id),model,name,location,count(model) as c FROM photos " \
              "GROUP BY model ORDER BY c desc) SELECT * FROM models WHERE c > 1;"
        return self.get_results_list(sql, 4)

    def get_photos(self):
        """get a list of photo galleries"""
        sql = "SELECT id,name,location FROM photos ORDER BY id desc;"
        return self.get_results_list(sql, 3)

    def get_site_galleries(self, site):
        """get a list of site galleries"""
        sql = f"SELECT id,name,location FROM photos WHERE site = '{site}' ORDER BY id desc"
        return self.get_results_list(sql, 3)

    def get_model_galleries(self, model):
        """get a list of model galleries"""
        sql = f"SELECT id,name,location FROM photos WHERE model = '{model}' ORDER BY id desc"
        return self.get_results_list(sql, 3)

    def get_all_videos(self):
        """get a list of all videos"""
        sql = f"SELECT * FROM videos ORDER BY id desc;"
        return self.get_results_list(sql, 9)

    def get_model_videos(self, model):
        """get a list of all videos for a model"""
        sql = f"SELECT * FROM videos WHERE model LIKE '{model}' ORDER BY id desc;"
        return self.get_results_list(sql, 9)

    def get_config(self):
        """"""
        sql = "SELECT * FROM config;"
        return self.get_results_list(sql, 6)[0]

#------------------------------------------------------------------------------
    def get_single_result(self, sql, cols):
        """"""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = [ None for x in range(cols) ]
        for row in cursor:
            result = row[:cols]
        return result

    def get_id(self, id):
        """"""
        sql = f"SELECT id,location FROM photos WHERE id='{id}';"
        return self.get_single_result(sql, 2)

    def get_photoset(self, id):
        """"""
        sql = f"SELECT * FROM photos WHERE id='{id}';"
        return self.get_single_result(sql, 6)

    def get_image_count(self, id):
        """"""
        sql = f"SELECT count FROM photos WHERE id = '{id}'"
        return self.get_single_result(sql, 1)[0]

    def get_video(self, id):
        """get a single video"""
        sql = f"SELECT * FROM videos WHERE id = {id};"
        return self.get_single_result(sql, 9)

    def get_next_prev_id(self, id, col=None, val=None):
        """"""
        query = ""
        if col is not None and val is not None:
            query = f"{col}='{val}' and "
        
        sql = f"SELECT id FROM photos WHERE {query} id %s {id} ORDER BY id %s LIMIT 1;"

        pid = self.get_single_result(sql % ('<', 'desc'), 1)[0]
        nid = self.get_single_result(sql % ('>', 'asc'), 1)[0]
    
        return pid, nid

    def get_next_prev_site(self, site, col=None, val=None):
        """"""
        sql = f"WITH sites as (SELECT DISTINCT id,site,location FROM photos WHERE id in " \
              f"(SELECT max(id) FROM photos GROUP BY site)) " \
              f"SELECT * FROM sites WHERE id %s (SELECT id FROM sites WHERE site='{site}') " \
              f"ORDER BY id %s LIMIT 1 ;"
        psite = self.get_single_result(sql % ('<', 'desc'), 3)[1]
        nsite = self.get_single_result(sql % ('>', 'asc'), 3)[1]
    
        return psite, nsite

    def get_next_prev_model(self, model, col=None, val=None):
        """"""
        sql = f"WITH models as (SELECT max(id) as mid,model,name,count(model) as c " \
              f"FROM photos GROUP BY model ORDER BY c %s) SELECT mid,model,name " \
              f"FROM models WHERE c %s (SELECT c FROM models WHERE model='{model}') " \
              f"ORDER BY c %s LIMIT 1 ;"
        pmodel = self.get_single_result(sql % ('desc','<','desc'), 3)[1]
        nmodel = self.get_single_result(sql % ('asc','>','asc'), 3)[1]
    
        return pmodel, nmodel

    def get_next_prev_video(self, video, col=None, val=None):
        """"""
        query = ""
        if col is not None and val is not None:
            query = f"{col}='{val}' and "
        
        sql = f"SELECT id FROM videos WHERE {query} id %s {video} ORDER BY id %s LIMIT 1;"
        pvideo = self.get_single_result(sql % ('<','desc'), 1)[0]
        nvideo = self.get_single_result(sql % ('>','asc'), 1)[0]
    
        return pvideo, nvideo

#------------------------------------------------------------------------------
#
class KindgirlsDB(BasicDB):
    
    def __init__(self):
        pass
        
    def createdb(self, drop=False):
        """"""
        cursor = self.conn.cursor()
        # get the count of tables with the name
        cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='kindgirls' ''')

        # if the count is 1, then table exists
        if cursor.fetchone()[0] == 1 : 
            print('Table exists.')
            if drop:
                print("Drop Table")
                self.conn.execute('''DROP TABLE kindgirls;''')
            else:
                return

        self.conn.execute('''CREATE TABLE kindgirls
            (id        INT PRIMARY KEY   NOT NULL,
             name          CHAR(256)     NOT NULL,
             location      CHAR(256)     NOT NULL,
             site          CHAR(50)      NOT NULL,
             model         CHAR(50)      NOT NULL,
             count         INT
             );''')

    def delete_id(self, id):
        """"""
        sql = f"DELETE FROM photos WHERE id = '{id}'"
        conn.execute(sql)
        conn.commit()


    def add_update_row(self, id, name, location, count):
        """"""
        # need test for pre-existing row
        i,l = self.get_id(id)
        if l == None:
            # insert new row
            site = location.split('/')[0]
            model = ''.join(filter(lambda x: not x.isdigit(), name)).replace('_',' ').strip()
            sql = f"INSERT INTO kindgirls (id,name,location,site,model,count) VALUES ('{id}', '{name}', '{location}', '{site}', '{model}', {count})"
            print(sql)
            self.conn.execute(sql)
            self.conn.commit()
        else:
            pass
            # update existing row
            #site = location.split('/')[0]
            #sql = f"UPDATE KINDGIRLS set name = '{name}', location = '{location}', site = '{site}', model = '{model}', count = {count} WHERE id = '{id}'"
            #print(sql)
            #self.conn.execute(sql)
            #self.conn.commit()

def load_db():
    """"""
    kdb = KindgirlsDB()
    kdb.conn = connectdb()
    kdb.createdb(True)
    
    with open('/Users/judge/Pictures/kindgirls/gals.kindgirls.com/flask/static/data.csv', 'r') as fp:
        lines = fp.read().split()
        for l in lines:
            d = l.split(',')
            kdb.add_update_row(int(d[0]), d[1], d[2])

    cursor = kdb.conn.cursor()
    sql = f"SELECT count(name) FROM photos"
    cursor.execute(sql)
    print(f"Rows inserted - {cursor.fetchone()[0]}")


def upgrade_db_2():
    """"""
    kdb = KindgirlsDB()
    kdb.connectdb()

    cursor = kdb.cursor()
    #sql = "ALTER kindgirls RENAME TO oldkindgirls;"
    sql = '''CREATE TABLE newkindgirls
            (id        INT PRIMARY KEY   NOT NULL,
             name          CHAR(256)     NOT NULL,
             location      CHAR(256)     NOT NULL,
             site          CHAR(50)      NOT NULL,
             model         CHAR(50)      NOT NULL,
             count         INT           
             );'''
    kdb.execute(sql)
    kdb.commit()

    rootdir = "/Users/judge/Pictures/kindgirls/gals.kindgirls.com"
    sql = "SELECT id,name,location,site FROM photos;"
    cursor.execute(sql)
    for row in cursor:
        id,name,location,site = row
        model = ''.join(filter(lambda x: not x.isdigit(), name)).replace('_',' ').strip()
        count = len(glob.glob(f"{rootdir}/{location}/*.jpg"))
        print(f"{count} {model} {location}")
        sql = f"INSERT INTO newkindgirls (id,name,location,site,model,count) VALUES ('{id}', '{name}', '{location}', '{site}', '{model}', {count})"
        kdb.execute(sql)
        kdb.commit()

 
def upgrade_db_1():
    """"""
    kdb = KindgirlsDB()
    kdb.connectdb()
    stuff = []

    cursor = kdb.cursor()
    sql = f"SELECT id,name,location FROM photos;"
    cursor.execute(sql)
    for row in cursor:
        id, name, location = row
        site = location.split('/')[0]
        print(f"{id} {site} {name} {location}")
        stuff.append((id, name, location, site))

    print(len(stuff))

    for line in stuff:
        id, name, location, site = line
        sql = f"UPDATE photos SET site='{site}' WHERE id='{id}'"
        kdb.execute(sql)
        kdb.commit()


def testing():
    # test create and insert row
    kdb = KindgirlsDB()
    kdb.connectdb(database='test.db')
    kdb.createdb(True)
    
    kdb.add_update_row(531, 'sandra_shine5', 'Twistys/sandra_shine5', 15)
    kdb.add_update_row(531, 'sandra_shine5', 'metart/sandra_shine5',  16)
    kdb.add_update_row(541, 'sandra_shine6', 'metart/sandra_shine6',  15)
    kdb.add_update_row(561, 'sandra_shine7', 'Twistys/sandra_shine7', 12)

    print(kdb.get_id(531))
    
    print(kdb.get_id(532))

    print(kdb.get_next_prev_id(531))
    print(kdb.get_next_prev_id(541))
    
    print(kdb.get_sites())
    print(kdb.get_site_galleries('metart'))
    print(kdb.get_image_count(561))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "-upgrade":
            upgrade_db()
        elif sys.argv[1] == "-load":
            load_db()
        elif sys.argv[1] == "-testing":
            testing()
    else:
        print("options -upgrade or -load or -testing")

