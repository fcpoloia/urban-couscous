
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

import glob
from flask import render_template, request
from flask.views import View

from flaskr.common.utils import random_selection
from flaskr.pages.base import HtmlSite
from flaskr.database.utils import DatabaseTables, get_config
from flaskr.database.errors import DatabaseMissingError

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


class RootPageView(CommonView):

    def dispatch_request(self, dbname):
        """"""
        mysite = HtmlRootPage(dbname)
        mysite.heading()
        return mysite.rootpage()


# HtmlPages

class HtmlSearchPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def search(self, term):
        """list all photo sets, videos, models and sites that match search term"""
        #order = self.get_order("search")
        #term = term.replace(' ','%')

        modeldicts, galldicts, viddicts, sitedicts = self.search_all_tables(term.replace(' ','%'))

        #self.heading()
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(f"Search Results for '{term}'", True, 'search') #,self.links)
        page_dict['search'] = True

        return render_template("search_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               search_term=term,
                               galldicts=galldicts,
                               modeldicts=modeldicts,
                               sitedicts=sitedicts,
                               viddicts=viddicts)


class HtmlRandomPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def random(self):
        """list a short random list of photo sets, videos, models and sites"""
        modeldicts = self.moddict(random_selection(self.db.models_table().select_all(), 7))
        galldicts = self.galdict(random_selection(self.db.photos_table().select_all(), 10))
        viddicts = self.viddict(random_selection(self.db.videos_table().select_all(), 4))

        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('Random Selection',True,'random') #,self.heading())
        page_dict['search'] = True

        return render_template("search_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts,
                               modeldicts=modeldicts,
                               viddicts=viddicts,
                               pagetype='random')


class HtmlRootPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def rootpage(self):
        """landing page"""
        buttons = [
            {'href':f"/photos/{self.dbname}/", 'name':'Photos'},
            {'href':f"/models/{self.dbname}/", 'name':'Models'},
            {'href':f"/sites/{self.dbname}/",  'name':'Sites'},
            {'href':f"/videos/{self.dbname}/", 'name':'Videos'},
        ]

        # title plaintitle heading type
        page_dict = self.init_page_dict('',True,'') #,self.heading())
        page_dict['button_class'] = 'fourbuttons'

        return render_template("intro.html",
                               webroot=get_config(self.dbname)['webroot'],
                               page=page_dict,
                               buttons=buttons)


class HtmlRandomAll(HtmlSite):
    """pick random entries from all the databases"""

    def __init__(self):
        """"""
        super().__init__()

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
            modeldicts = self.moddict(random_selection(self.db.models_table().select_all(), 1))
            galldicts = self.galdict(random_selection(self.db.photos_table().select_all(), 1))
            viddicts = self.viddict(random_selection(self.db.videos_table().select_all(), 1))
            #m,g,v = self.random_table()
            mods = mods + modeldicts
            gals = gals + galldicts
            vids = vids + viddicts


        # title plaintitle heading type | navigation db
        page_dict = {
            'title': "Random Selection From All",
            'heading':'Stuff',
            'plaintitle':True,
        }

        return render_template("search_page.html",
                               webroot="http://"+request.host.replace(':5000',''),
                               page=page_dict,
                               galldicts=gals,
                               modeldicts=mods,
                               viddicts=vids,
                               pagetype='random')


class HtmlSearchAll(HtmlSite):
    """search all databases"""

    def __init__(self):
        """"""
        super().__init__()


    def search(self, term):
        """"""
        #term = term.replace(' ','%')
        mods = []
        gals = []
        vids = []
        sits = []
        for database in glob.glob("flaskr/sqlitedb/old_*.db") + glob.glob("flaskr/sqlitedb/new_*.db"):
            dbname = database.replace('flaskr/sqlitedb/new_','').replace('flaskr/sqlitedb/old_','').replace('.db','')
            self.set_dbname(dbname)
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                #error_occured = True
                raise
            m,g,v,s = self.search_all_tables(term.replace(' ','%'))
            mods = mods + m
            gals = gals + g
            vids = vids + v
            sits = sits + s

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
                               galldicts=gals,
                               modeldicts=mods,
                               sitedicts=sits,
                               viddicts=vids)

