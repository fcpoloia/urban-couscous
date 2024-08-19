
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

import glob
from flask import render_template, request, current_app
from flask.views import View

from flaskr.common.utils import random_selection
from flaskr.pages.base import HtmlSite, TileBuilder
from flaskr.database.utils import DatabaseTables, get_config
from flaskr.database.errors import DatabaseMissingError
from flaskr.collections import DBItems


#@app.route("/<dbname>/search", methods=['POST', 'GET'])
#def search(dbname):
#    """"""
#    term = get_search_term()
#    mysite = dbpage_factory('search',dbname)
#    mysite.set_thumb_size()
#    return mysite.search(term)

#@app.route("/<dbname>/random")
#def random(dbname):
#    """"""
#    mysite = dbpage_factory('random',dbname) #HtmlRandom(dbname)
#    mysite.set_thumb_size()
#    return mysite.random()

def get_search_term():
    """"""
    s = None
    if request.method == 'GET':
        s = request.args.get('search')
    return s


# Views

class CommonView(View):
    methods = ["POST", "GET"]

    def __init__(self):
        """"""

class DBSearchPageView(CommonView):

    def dispatch_request(self, dbname):
        """"""
        term = get_search_term()
        mysite = HtmlSearchPage(dbname)
        mysite.set_thumb_size()
        mysite.heading()
        return mysite.search(term)


class DBRandomPageView(CommonView):

    def dispatch_request(self, dbname):
        """"""
        mysite = HtmlRandomPage(dbname)
        mysite.set_thumb_size()
        mysite.heading()
        return mysite.random()


class RandomPageView(CommonView):

    def dispatch_request(self):
        """"""
        mysite = HtmlRandomAll()
        return mysite.random()


class SearchPageView(CommonView):

    def dispatch_request(self):
        """"""
        term = get_search_term()
        mysite = HtmlSearchAll()
        return mysite.search(term)


# class RootPageView(CommonView):

#     def dispatch_request(self, dbname):
#         """"""
#         mysite = HtmlRootPage(dbname)
#         mysite.heading()
#         return mysite.rootpage()


# HtmlPages

class HtmlSearchPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self._dbitems = DBItems()
        self._tiles = []

    def search_all_tables(self, term):
        """"""
        self._dbitems.addSiteMembers(self.db.sites_table().select_where_like('name', term))
        self._dbitems.addModelMembers(self.db.models_table().select_where_like('name', term))
        self._dbitems.addPhotoMembers(self.db.photos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc'))
        self._dbitems.addVideoMembers(self.db.videos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc'))

    def _build(self):
        """still need to support pages"""
        sidx = 0
        eidx = len(self._dbitems)
        
        iterator = list(self._dbitems)

        tile_bldr = TileBuilder(self.dbname)
        for elem in iterator[sidx:eidx]:
            #print(elem)
            self._tiles.append(tile_bldr.build_tile(elem)) #, filterurl=f"/{self._page}/{self._index}")) # optionally takes filterurl # 

    def search(self, term):
        """list all photo sets, videos, models and sites that match search term"""
        #order = self.get_order("search")
        #term = term.replace(' ','%')

        self.search_all_tables(term.replace(' ','%'))
        self._build()

        #self.heading()
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(f"Search Results for '{term}'", True, 'search') #,self.links)
        page_dict['search'] = True

        return render_template("search_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               search_term=term,
                               tiles=self._tiles
                               #galldicts=galldicts,
                               #modeldicts=modeldicts,
                               #sitedicts=sitedicts,
                               #viddicts=viddicts
                               )


class HtmlRandomPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self._dbitems = DBItems()
        self._tiles = []

    def _build(self):
        """still need to support pages"""
        sidx = 0
        eidx = len(self._dbitems)
        
        iterator = list(self._dbitems)

        tile_bldr = TileBuilder(self.dbname)
        for elem in iterator[sidx:eidx]:
            #print(elem)
            self._tiles.append(tile_bldr.build_tile(elem)) #, filterurl=f"/{self._page}/{self._index}")) # optionally takes filterurl # 

    def random(self):
        """list a short random list of photo sets, videos, models and sites"""
        self._dbitems.addModelMembers(random_selection(self.db.models_table().select_all(), 7))
        self._dbitems.addPhotoMembers(random_selection(self.db.photos_table().select_all(), 10))
        self._dbitems.addVideoMembers(random_selection(self.db.videos_table().select_all(), 8))

        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('Random Selection',True,'random') #,self.heading())
        page_dict['search'] = True

        self._build()

        return render_template("search_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               tiles=self._tiles,
                               #galldicts=galldicts,
                               #modeldicts=modeldicts,
                               #viddicts=viddicts,
                               pagetype='random')


# class HtmlRootPage(HtmlSite):

#     def __init__(self, dbname):
#         """"""
#         super().__init__(dbname)


#     def rootpage(self):
#         """landing page"""
#         buttons = [
#             {'href':f"/photos/{self.dbname}/", 'name':'Photos'},
#             {'href':f"/models/{self.dbname}/", 'name':'Models'},
#             {'href':f"/sites/{self.dbname}/",  'name':'Sites'},
#             {'href':f"/videos/{self.dbname}/", 'name':'Videos'},
#         ]

#         # title plaintitle heading type
#         page_dict = self.init_page_dict('',True,'') #,self.heading())
#         page_dict['button_class'] = 'fourbuttons'


#         return render_template("intro.html",
#                                webroot=get_config(self.dbname)['webroot'],
#                                page=page_dict,
#                                buttons=buttons)


class HtmlRandomAll(HtmlSite):
    """pick random entries from all the databases"""

    def __init__(self):
        """"""
        super().__init__()
        self._dbitems = DBItems()
        self._dbtiles = {'model':[], 'photo':[], 'video':[]}


    def random(self):
        """"""
        mods = []
        gals = []
        vids = []
        for database in glob.glob("flaskr/sqlitedb/old_*.db") + glob.glob("flaskr/sqlitedb/new_*.db"):
            dbname = database.replace('flaskr/sqlitedb/new_','').replace('flaskr/sqlitedb/old_','').replace('.db','')
            self.set_dbname(dbname)
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                #error_occured = True
                raise

            # now get a single random model, photo and video from each database

            self._dbtiles[dbname] = []
            tile_bldr = TileBuilder(self.dbname)
            try:
                self._dbtiles['model'].append(tile_bldr.build_tile( (random_selection(self.db.models_table().select_all(), 1)[0], 'model') )) 
            except:
                pass
            try:
               self._dbtiles['photo'].append(tile_bldr.build_tile( (random_selection(self.db.photos_table().select_all(), 1)[0], 'photo') )) 
            except:
                pass
            try:
               self._dbtiles['video'].append(tile_bldr.build_tile( (random_selection(self.db.videos_table().select_all(), 1)[0], 'video') )) 
            except:
                pass

        tiles = self._dbtiles['model'] + self._dbtiles['photo'] + self._dbtiles['video']

        # title plaintitle heading type | navigation db
        page_dict = {
            'title': "Random Selection From All",
            'heading':'Stuff',
            'plaintitle':True,
        }

        return render_template("search_page.html",
                               webroot="http://"+request.host.replace(':5000',''),
                               page=page_dict,
                               tiles=tiles,
                               #galldicts=gals,
                               #modeldicts=mods,
                               #viddicts=vids,
                               pagetype='random')


class HtmlSearchAll(HtmlSite):
    """search all databases"""

    def __init__(self):
        """"""
        super().__init__()
        self._dbtiles = {'model':[], 'photo':[], 'video':[], 'site':[]}


    def search(self, term):
        """"""
        tiles = []
        #term = term.replace(' ','%')
        for database in glob.glob("flaskr/sqlitedb/old_*.db") + glob.glob("flaskr/sqlitedb/new_*.db"):
            dbname = database.replace('flaskr/sqlitedb/new_','').replace('flaskr/sqlitedb/old_','').replace('.db','')
            self.set_dbname(dbname)
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                #error_occured = True
                raise

            dbitems = DBItems()
            dbitems.addSiteMembers(self.db.sites_table().select_where_like('name', term))
            dbitems.addModelMembers(self.db.models_table().select_where_like('name', term))
            dbitems.addPhotoMembers(self.db.photos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc'))
            dbitems.addVideoMembers(self.db.videos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc'))

            iterator = list(dbitems)

            tile_bldr = TileBuilder(self.dbname)
            for item in iterator:
                tiles.append(tile_bldr.build_tile(item))


        ordered_tiles = []
        ordered_tiles += [t for t in tiles if t['kind'] == "model"] 
        ordered_tiles += [t for t in tiles if t['kind'] == "photo"] 
        ordered_tiles += [t for t in tiles if t['kind'] == "video"] 
        ordered_tiles += [t for t in tiles if t['kind'] == "site"] 

        # title plaintitle heading type | navigation db
        page_dict = {
            'title': f"Search Results for '{term}'",
            'heading':'Stuff',
            'plaintitle':True,
            'button_class':'fivebuttons'
        }

        return render_template("search_page.html",
                               webroot="http://"+request.host.replace(':5000',''),
                               page=page_dict,
                               search_term=term,
                               tiles=ordered_tiles,
                               #galldicts=gals,
                               #modeldicts=mods,
                               #sitedicts=sits,
                               #viddicts=vids
                               )

