
import os
import glob
from flask import request

from flaskr.database.sql import ConfigTable, SortTable, ModelsTable, SitesTable, PhotosTable, VideosTable


def database_buttons():
    """"""
    sql = "SELECT title FROM config;"
    obuttons = []
    nbuttons = []
    names = []
    dblist = {}
    for database in glob.glob("flaskr/sqlitedb/old_*.db"):
        dbname = database.replace('flaskr/sqlitedb/old_','').replace('.db','')
        name = ConfigTable(database).get_single_result(sql,1)[0]
        dblist[dbname] = name
        names.append(dbname)
    names.sort()
    for dbname in names:
        obuttons.append({'href':'/'+dbname+'/random', 'name':dblist[dbname]})

    names = []
    for database in glob.glob("flaskr/sqlitedb/new_*.db"):
        dbname = database.replace("flaskr/sqlitedb/new_",'').replace('.db','')
        name = ConfigTable(database).get_single_result(sql,1)[0]
        dblist[dbname] = name
        names.append(dbname)
    names.sort()
    for dbname in names:
        nbuttons.append({'href':'/'+dbname+'/random', 'name':dblist[dbname]})


    page_dict = {
        'title':'',
        'heading':'Stuff',
        'plaintitle':True,
        'button_class':'fivebuttons'
    }
    return obuttons, nbuttons, page_dict


class Database:
    def __init__(self, dbname):
        """"""
        self.dbname = dbname
        self._dbpath = self.get_db_path()

    def get_db_path(self):
        """"""
        old = f"flaskr/sqlitedb/old_{self.dbname}.db"
        new = f"flaskr/sqlitedb/new_{self.dbname}.db"
        path = ""
        if os.path.exists(old):
            path = old
        if os.path.exists(new):
            path = new
        return path

    @property
    def dbpath(self):
        return self._dbpath

    @dbpath.setter
    def dbpath(self, path):
        self._dbpath = path


class DatabaseTables:
    """"""
    def __init__(self, dbname):
        """"""
        self.db = Database(dbname)

    def models_table(self):
        return ModelsTable(self.db.dbpath)

    def photos_table(self):
        return PhotosTable(self.db.dbpath)

    def videos_table(self):
        return VideosTable(self.db.dbpath)

    def sites_table(self):
        return SitesTable(self.db.dbpath)

    def config_table(self):
        return ConfigTable(self.db.dbpath)

    def sort_table(self):
        return SortTable(self.db.dbpath)


def get_config(dbname):
    """Read Config Table"""
    dbt = DatabaseTables(dbname)
    try:
        vals = dbt.config_table().select_all()[0]
        cols = dbt.config_table().column_list()
        config = {}
        if len(vals) == len(cols):
            for i, col in enumerate(cols): #range(len(cols)):
                config[col] = vals[i]
        #print(config)
    except DatabaseMissingError:
        raise
    # fix the webroot so that it copes with both name or ip provided in url
    config['webroot'] = "http://"+request.host.replace(':5000','')
    # append more items
    config['thumbsize'] = 240
    config['thumb_h'] = 240
    config['pgcount'] = 500
    config['vpgcount'] = 100

    return config




#------------------------------------------------------------------------------
# select(cols).from(table).where(clause).group_by(col).order_by(col).desc()
# select().star().from(table).where(clause).group_by(col).order_by(col).asc()
#
class Query:
    """"""
    def __init__(self):
        """"""
        self.sql = ""

    def select(self, cols):
        """"""
        self.sql += f"select {cols}"
        return self

    def frm(self, table):
        """"""
        self.sql += f" from {table}"
        return self

    def where(self, clause):
        """"""
        self.sql += f" where {clause}"
        return self

    def group_by(self, col):
        """"""
        self.sql += f" group by {col}"
        return self

    def order_by(self, col):
        """"""
        self.sql += f" order by {col}"
        return self

    def desc(self):
        """"""
        self.sql += " desc"
        return self

    def asc(self):
        """"""
        self.sql += " asc"
        return self

    def __call__(self):
        """"""
        return self.sql


