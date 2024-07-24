

import glob
from flask import render_template, request

from flaskr.common.utils import random_selection
from flaskr.pages.base import HtmlSite
from flaskr.database.utils import get_config, DatabaseTables, DatabaseMissingError


class HtmlSearchPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def search(self, term):
        """list all photo sets, videos, models and sites that match search term"""
        #order = self.get_order("search")
        #term = term.replace(' ','%')

        modeldicts, galldicts, viddicts, sitedicts = self.search_all_tables(term.replace(' ','%'))

        links = self.heading()
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(f"Search Results for '{term}'",True,'search',links)
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
        page_dict = self.init_page_dict('Random Selection',True,'random',self.heading())
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
            {'href':f"/{self.dbname}/photos", 'name':'Photos'},
            {'href':f"/{self.dbname}/models", 'name':'Models'},
            {'href':f"/{self.dbname}/sites",  'name':'Sites'},
            {'href':f"/{self.dbname}/videos", 'name':'Videos'},
        ]

        # title plaintitle heading type
        page_dict = self.init_page_dict('',True,'',self.heading())
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
        for database in glob.glob("flaskr/old_*.db") + glob.glob("flaskr/new_*.db"):
            dbname = database.replace('flaskr/new_','').replace('flaskr/old_','').replace('.db','')
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
        for database in glob.glob("flaskr/old_*.db") + glob.glob("flaskr/new_*.db"):
            dbname = database.replace('flaskr/new_','').replace('flaskr/old_','').replace('.db','')
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

