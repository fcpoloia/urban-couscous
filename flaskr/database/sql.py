#!/usr/bin/env python3

# pylint: disable-msg=line-too-long
# pylint: disable-msg=empty-docstring

#
# tables - config, photos, videos, models, sites
#
# select * from config;
# pragma table_info(config);
#

"""
"""



from flaskr.database.connection import ConnectDB


#------------------------------------------------------------------------------
class Table(ConnectDB):
    """"""
    def __init__(self, dbname, tblname, columns):
        """"""
        super().__init__()
        self.name = tblname
        self.columns = columns
        self.sql_all = f"SELECT {','.join(self.columns)} FROM {self.name} "
        self.pragma = f"pragma table_info({self.name});"
        self.connectdb(dbname)

    def col_count(self):
        """"""
        return len(self.get_results_list(self.pragma, 6))

    def row_count(self):
        """"""
        sql = f"SELECT COUNT() FROM {self.name};"
        return self.get_single_result(sql, 1)[0]

    def column_list(self):
        """"""
        res = self.get_results_list(self.pragma, 2)
        columns = []
        for col in res:
            columns.append(col[1])
        return columns

    def select_all(self):
        """"""
        return self.get_results_list(self.sql_all, self.col_count())

    def select_where(self, column, value):
        """"""
        sql = self.sql_all + f"where {column} = '{value}' "
        return self.get_results_list(sql, self.col_count())

    def select_order_by(self, order_col, direction):
        """"""
        sql = self.sql_all + f"order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())

    def select_group_by_order_by(self, group_col, order_col, direction):
        """"""
        sql = self.sql_all + f" group by {group_col} order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())

    def select_where_order_by(self, column, value, order_col, direction):
        """"""
        sql = self.sql_all + f"where {column} = '{value}' order by {order_col} COLLATE NOCASE {direction} "
        return self.get_results_list(sql, self.col_count())

    def select_where_group_by(self, column, value, group_col):
        """"""
        sql = self.sql_all + f"where {column} = '{value}' group by {group_col} COLLATE NOCASE "
        return self.get_results_list(sql, self.col_count())

    # pylint: disable-msg=too-many-arguments
    def select_where_group_by_order_by(self, column, value, group_col, order_col, direction):
        """"""
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

    #def nn():
    #    """"""
    #    sql="select count(models.id),models.id,models.name,photos.model_id,videos.model_id from models join photos on photos.model_id=models.id join videos on videos.model_id=models.id group by models.id order by count(models.id) desc;"

    def get_next_prev(self, idx, col=None, val=None):
        """"""
        query = ""
        if col is not None and val is not None:
            query = f"{col}='{val}' and "

        sql = f"SELECT id FROM {self.name} WHERE {query} id %s {idx} ORDER BY id %s LIMIT 1;"
        pid = self.get_single_result(sql % ('<','desc'), 1)[0]
        nid = self.get_single_result(sql % ('>','asc'), 1)[0]
        pn = nn = ''
        if pid is not None:
            pn = self.get_single_result(f"select name from {self.name} where id = {pid}", 1)[0]
        if nid is not None:
            nn = self.get_single_result(f"select name from {self.name} where id = {nid}", 1)[0]
        return nid, pid, nn, pn

    def select_where_like(self, column, value):
        """"""
        sql = self.sql_all + f"where {column} like '%{value}%'" # group by id order by id desc"
        return self.get_results_list(sql, self.col_count())

    # pylint: disable-msg=too-many-arguments
    def select_where_like_group_order(self, column, value, group, order, direction):
        """"""
        sql = self.sql_all + f"where {column} like '%{value}%' group by {group} order by {order} COLLATE NOCASE {direction}"
        return self.get_results_list(sql, self.col_count())


# get a list of model names ordered by set count

#------------------------------------------------------------------------------
class ModelsTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','name','thumb']
        super().__init__(dbname, 'models', self.columns)

    def select_models_by_count(self, order):
        """finally a simpler statement to get a list of models with a count of pset+vids"""
        sql = f"with mc as (select model_id from photos union all select model_id from videos) " \
              f"select model_id,models.name,models.thumb,count(model_id) as c from mc join models on models.id=mc.model_id group by model_id order by c {order};"
        return self.get_results_list(sql, self.col_count())

    def get_model_set_count(self):
        """sum of photosets and videos grouped by model id"""
        sqlp = "select models.id,count(photos.model_id) from models left join photos on photos.model_id=models.id group by models.id ;"
        sqlv = "select models.id,count(videos.model_id) from models left join videos on videos.model_id=models.id group by models.id ;"
        models = {}
        for idx, count in self.get_results_list(sqlp, 2):
            models[idx] = count
        for idx, count in self.get_results_list(sqlv, 2):
            models[idx] = count + models[idx]
        return models

class SitesTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','name','location']
        super().__init__(dbname, 'sites', self.columns)

    def old_select_sites_by_count(self, order):
        """list sites by largest count of combined photosets and videos"""

        sql = f"select sites.id,sites.name,sites.location,count(sites.id) from sites left join photos on photos.site_id=sites.id group by sites.id " \
              f" union all select sites.id,sites.name,sites.location,count(sites.id)  from sites " \
              f"left join videos on videos.site_id=sites.id where sites.id is null group by sites.id order by count(sites.id) {order} ;"
        result = self.get_results_list(sql, self.col_count())
        #print(f"{len(result)} {result}")
        return result

    def select_sites_by_count(self, order):
        """finally a simpler statement to get a list of sites with a count of pset+vids"""
        sql = f"with mc as (select site_id from photos union all select site_id from videos) " \
              f"select site_id,sites.name,sites.location,count(site_id) as c from mc join sites on sites.id=mc.site_id group by site_id order by c {order};"
        return self.get_results_list(sql, self.col_count())

    def get_sites_set_count(self):
        """sum of photosets and videos grouped by model id"""
        sqlp = "select sites.id,count(photos.site_id) from sites left join photos on photos.site_id=sites.id group by sites.id ;"
        sqlv = "select sites.id,count(videos.site_id) from sites left join videos on videos.site_id=sites.id group by sites.id ;"
        sites = {}
        for idx, count in self.get_results_list(sqlp, 2):
            sites[idx] = count
        for idx, count in self.get_results_list(sqlv, 2):
            sites[idx] = count + sites[idx]
        return sites

class PhotosTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','model_id','site_id','name','location','thumb','count','pdate']
        super().__init__(dbname, 'photos', self.columns)

class VideosTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','model_id','site_id','name','filename','thumb','poster','width','height','length','vdate']
        super().__init__(dbname, 'videos', self.columns)

class ConfigTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','webroot','rootpath','title','images','thumbs','videos','thumbs0','models']
        super().__init__(dbname, 'config', self.columns)


class SortTable(Table):
    """"""
    def __init__(self, dbname):
        """"""
        self.columns = ['id','photos','models','model','videos','sites','site','search']
        super().__init__(dbname, 'default_sort', self.columns)



#------------------------------------------------------------------------------

# we need an insert query to add photo set or video that can establish site_id and model_id

#------------------------------------------------------------------------------

"""
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
    stmt = q.select('*').frm('photos').where("name like '%mango%'")()
    rslts = b.get_results_list(stmt, b.num_cols('photos'))
    print(len(rslts))
    for rslt in rslts:
        print(rslt)

    s = SitesTable(DATABASE)
    print("select sites by count")
    print(s.select_sites_by_count('desc'))
"""

