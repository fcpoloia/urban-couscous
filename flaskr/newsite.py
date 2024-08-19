
""""""

# pylint: disable-msg=empty-docstring,line-too-long,trailing-whitespace

from flask import current_app, render_template, session, request
from flask.views import View

from flaskr.pages.base import do_post_get, get_page_num, TileBuilder
from flaskr.pages.sorttypes import sorting, vsorting
from flaskr.collections import DBItems
from flaskr.database.utils import get_config, DatabaseTables


class DBNewSiteView(View):
    """this should be common to all pages that are of the /<page>/<dbname> form"""
    methods = ["POST", "GET"]

    def __init__(self, page=''):
        """"""
        self._page = page
        current_app.logger.info(f"DBNewSiteView - {page}")

    def dispatch_request(self, dbname):
        """
        open database
        query database for all sites, returning a list of sites
        convert list items to href,src,label
        build title/navigation line
        """
        do_post_get() # read get request and store in session array
        items = ItemBuilder(dbname, self._page)
        page = HtmlBuilder(items.get(), dbname, self._page)
        return page.html()


class DBNewSiteIdView(View):  # /models/<dbname>/<id>  /sites/<dbname>/<id>
    """this should be common to all pages that are of the /<page>/<dbname>/<id> form"""
    methods = ["POST", "GET"]

    def __init__(self, page=''):
        """"""
        self._page = page
        current_app.logger.info(f"DBNewSiteIdView - {page}")

    def dispatch_request(self, dbname, index):
        """
        get list of items
            open database
            query database for site id, returning a list of photosets and videos
        convert list items to href,src,label
        build title/navigation line
        """
        do_post_get() # read get request and store in session array
        items = IndexedItemBuilder(dbname, self._page, index)
        page = IndexedHtmlBuilder(items.get(), dbname, index, self._page)
        return page.html()
    

class ItemBuilder:
    """"""
    def __init__(self, dbname, page):
        self._db = DatabaseTables(dbname)
        self._dbname = dbname
        self._page = page
        self._dbitems = DBItems()


    def get_order(self):
        """"""
        if 'order' in session:
            order = session['order']
        else:
            # get default from db
            sql = f"SELECT {self._page} FROM default_sort;"
            order = self._db.sort_table().get_single_result(sql,1)[0]

        return order


    def get(self):
        """"""
        order = self.get_order()
        dbquery = DatabaseItemQuery(self._dbname)
        current_app.logger.info(f"ItemBuilder - _page = {self._page}")
        if self._page == 'models':
            dbquery.get_models_items(order)
        elif self._page == 'photos':
            dbquery.get_photos_items(order)
        elif self._page == 'videos':
            dbquery.get_videos_items(order)
        elif self._page == 'sites':
            dbquery.get_sites_items(order)
        return dbquery.get_dbitems()


class IndexedItemBuilder:
    """"""
    def __init__(self, dbname, page, index):
        self._db = DatabaseTables(dbname)
        self._dbname = dbname
        self._index = index
        self._page = page
        self._dbitems = DBItems()

    def get_order(self):
        """"""
        if 'order' in session:
            order = session['order']
        else:
            # get default from db - This should be in a database class
            sql = f"SELECT {self._page} FROM default_sort;"
            order = self._db.sort_table().get_single_result(sql,1)[0]

        return order


    def get(self):
        """"""
        order = self.get_order()
        dbquery = DatabaseItemQuery(self._dbname)
        if self._page == 'site':
            dbquery.get_site_items(order, self._index)
        elif self._page == 'model':
            dbquery.get_model_items(order, self._index)
        return dbquery.get_dbitems()




class IndexedHtmlBuilder:
    """"""
    def __init__(self, items, dbname, index, page):
        """"""
        self._items = items
        self._dbname = dbname
        self.config = get_config(dbname)
        self._index = index
        self._tiles = []
        self._page = page
        self._build()

    def _build(self):
        """still need to support pages"""
        #sidx = 0
        #eidx = len(self._items)
        sidx, eidx = self.page_range(get_page_num(1), len(self._items))
        
        iterator = list(self._items)

        tile_bldr = TileBuilder(self._dbname)
        for elem in iterator[sidx:eidx]:
            #print(elem)
            self._tiles.append(tile_bldr.build_tile(elem, filterurl=f"/{self._page}/{self._index}")) # optionally takes filterurl # 

    def page_range(self, num, total, pgcount=0):
        """"""
        if pgcount == 0:
            pgcount = self.config['pgcount']
        self.pg = {'next': num+1 if (num * pgcount) < total else 0,
                   'prev': num-1 if (num - 1) > 0 else 0}
        current_app.logger.debug(f"{self.pg}")
        return (num-1)*pgcount, (num*pgcount)
    
    def page_nav(self):
        """"""
        nav = Navigation(self._dbname, self._page, self.pg)
        return nav.page_nav(self._index)
    
    def html(self):
        """"""
        return render_template("photos_and_videos_page.html",
                               webroot=self.config['webroot'],
                               page=self.page_nav(),
                               tiles=self._tiles
                               )


class HtmlBuilder:
    """"""
    def __init__(self, items, dbname, page):
        """"""
        self._items = items
        self._dbname = dbname
        self.config = get_config(dbname)
        self._page = page
        self._tiles = []
        self.pg = {'next':-1, 'prev':-1}
        self._build()


    def _build(self):
        """still need to support pages"""
        #sidx = 0
        #eidx =  min(len(self._items), 500)
        sidx, eidx = self.page_range(get_page_num(1), len(self._items))

        current_app.logger.info(f"HtmlBuilder - len(_items) = {eidx}")

        iterator = list(self._items)
        current_app.logger.info("HtmlBuilder - iterator created")

        tile_bldr = TileBuilder(self._dbname)
        for elem in iterator[sidx:eidx]:
            self._tiles.append(tile_bldr.build_tile(elem)) # optionally takes filterurl
        current_app.logger.info(f"HtmlBuilder - {len(self._tiles)} tiles created")


    def page_range(self, num, total, pgcount=0):
        """"""
        if pgcount == 0:
            pgcount = self.config['pgcount']
        self.pg = {'next': num+1 if (num * pgcount) < total else 0,
                   'prev': num-1 if (num - 1) > 0 else 0}
        current_app.logger.debug(f"{self.pg}")
        return (num-1)*pgcount, (num*pgcount)


    def page_nav(self):
        """"""
        nav = Navigation(self._dbname, self._page, self.pg)
        return nav.page_nav()


    def html(self):
        """"""
        html = "just_videos_page.html" if self._page == "videos" else "models_or_sites_page.html"
        current_app.logger.info("calling render_template()")
        return render_template(html,
                               webroot=self.config['webroot'],
                               page=self.page_nav(),
                               tiles=self._tiles
                               )


class Navigation:
    """this class needs to be generallised - ie. page agnostic"""

    def __init__(self, dbname, page, pg):
        """"""
        self._dbname = dbname
        self._db = DatabaseTables(dbname)
        self.config = get_config(dbname)

        self.pg = pg
        self.links = []
        self.heading(page)


    def heading(self, page=None):
        """"""
        self.links = {
            "photos": {"href": f"/photos/{self._dbname}/", "title": "Photos", 'class':'', 'rows': self._db.photos_table().row_count() },
            "models": {"href": f"/models/{self._dbname}/", "title": "Girls",  'class':'', 'rows': self._db.models_table().row_count() },
            "sites":  {"href": f"/sites/{self._dbname}/",  "title": "Sites",  'class':'', 'rows':  self._db.sites_table().row_count()-1 },
            "videos": {"href": f"/videos/{self._dbname}/", "title": "Videos", 'class':'', 'rows': self._db.videos_table().row_count() }
            }

        if page is not None:
            if page == "site":
                page = "sites"
            if page == "model":
                page = "models"
            self.links[page]['class'] = " w3-dark-grey "


    def page_nav(self, siteid=''):
        """plaintitle=True ptype=name pg links title='' """
        page_dict = {
            'title':'', 'db':self._dbname, 'heading':self.config['title'],
            'plaintitle':True, 'navigation':self.links, 'type':'site', 'pg':self.pg,
            'url': request.base_url
        }
        nsite, psite, nname, pname = (0,0,"","") #self._db.sites_table().get_next_prev(siteid)

        page_dict['nid'] = nsite
        page_dict['pid'] = psite
        page_dict['next'] = nname
        page_dict['prev'] = pname
        
        return page_dict 


class DatabaseItemQuery:
    """"""
    def __init__(self, dbname):
        """"""
        self._db = DatabaseTables(dbname)
        self._dbitems = DBItems()


    def get_dbitems(self):
        """"""
        return self._dbitems


    def get_site_items(self, order, index):
        """"""
        photos = self._db.photos_table().select_where_order_by("site_id", index, sorting[order][0], sorting[order][2])
        self._dbitems.addPhotoMembers(photos)
        videos = self._db.videos_table().select_where_order_by("site_id", index, vsorting[order][0], vsorting[order][2])
        self._dbitems.addVideoMembers(videos)


    def get_sites_items(self, order): # sites plural
        """"""
        order_by = {'most': 'desc', 'least': 'asc'}

        if order in ['most', 'least']:
            sites = self._db.sites_table().select_sites_by_count(order_by[order])
        else:
            sites = self._db.sites_table().select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
        self._dbitems.addSiteMembers(sites)


    def get_model_items(self, order, index): # model singular
        """"""
        order_by = {
            'alpha': 'asc',  'ralpha': 'desc',
            'id':    'asc',  'rid':    'desc',
            'date':  'asc',  'rdate':  'desc'
            }
        unsorted_photos = self._db.photos_table().select_where_group_by('model_id', index, 'id')
        #    id, model_id, site_id, name, location, thumb, count, pdate = gallery
        unsorted_videos = self._db.videos_table().select_where_group_by('model_id', index, 'id')

        photos = []
        videos = []
        # lambda is setting the database column to sort on - date is different between photos and videos
        if order in ('alpha', 'ralpha'):
            photos = sorted(unsorted_photos, key = lambda x: x[3]) #name
            videos = sorted(unsorted_videos, key = lambda x: x[3])
        elif order in ('id', 'rid'):
            photos = sorted(unsorted_photos, key = lambda x: x[0]) # id
            videos = sorted(unsorted_videos, key = lambda x: x[0])
        elif order in ('date', 'rdate'):
            try:
                photos = sorted(unsorted_photos, key = lambda x: x[7])  #pdate
                videos = sorted(unsorted_videos, key = lambda x: x[10]) #vdate
            except TypeError:
                # if database has no dates, then use id ordering
                photos = sorted(unsorted_photos, key = lambda x: x[0]) # id
                videos = sorted(unsorted_videos, key = lambda x: x[0])

        if order_by[order] == 'desc':
            photos.reverse()
            videos.reverse()

        self._dbitems.addPhotoMembers(photos)
        self._dbitems.addVideoMembers(videos)


    def get_models_items(self, order): # models plural
        """"""
        order_by = {
            'alpha':   'asc',   'ralpha':   'desc',
            'vlatest': 'desc',  'rvlatest': 'asc',
            'platest': 'desc',  'rplatest': 'asc',
            'most':    'desc',  'least':    'asc',
            'id':      'asc',   'rid':      'desc'
        }
        models = []
        if order in ['alpha', 'ralpha']:
            models = self._db.models_table().select_group_by_order_by('name', 'name', order_by[order])

        elif order in ['vlatest', 'rvlatest']:
            models = self._db.models_table().select_by_most_recent_videos('model_id', order_by[order])

        elif order in ['platest', 'rplatest']:
            models = self._db.models_table().select_by_most_recent_photos('model_id', order_by[order])

        elif order in ['most', 'least']:
            models = self._db.models_table().select_models_by_count(order_by[order])

        elif order in ['id', 'rid']:
            models = self._db.models_table().select_order_by('id', order_by[order])

        if len(models) == 0:
            models = self._db.models_table().select_order_by('id', 'desc')

        self._dbitems.addModelMembers(models)


    def get_videos_items(self, order):
        """"""
        items = self._db.videos_table().select_order_by(vsorting[order][1], vsorting[order][2])
        if len(items) == 0:
            items = self._db.videos_table().select_group_by_order_by('id', 'id', 'desc')
        self._dbitems.addVideoMembers(items)


    def get_photos_items(self, order):
        """"""
        items = self._db.photos_table().select_order_by(sorting[order][1], sorting[order][2])
        if len(items) == 0:
            items = self._db.photos_table().select_group_by_order_by('id', 'id', 'desc')
        self._dbitems.addPhotoMembers(items)

