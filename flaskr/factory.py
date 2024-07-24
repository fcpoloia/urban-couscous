#!/usr/bin/env python3

# pylint: disable-msg=line-too-long
# pylint: disable-msg=empty-docstring
# pylint: disable-msg=missing-class-docstring,missing-function-docstring
# pylint: disable-msg=unused-variable

"""
# Mark II verion of the website using a different database schema
"""

from flask import request, render_template, make_response

from flaskr.database.utils import DatabaseMissingError, InvalidDatabaseError, database_buttons

from flaskr.pages.photo import HtmlPhotosPage, HtmlPhotoSetPage
from flaskr.pages.video import HtmlVideosPage, HtmlVideoPage
from flaskr.pages.model import HtmlModelsPage, HtmlModelPage
from flaskr.pages.site  import HtmlSitesPage,  HtmlSitePage
from flaskr.pages.common import HtmlSearchPage, HtmlRandomPage, HtmlRootPage, HtmlRandomAll, HtmlSearchAll
from flaskr.pages.fs import HtmlFileSystem




def site_root():
    """"""
    obuttons, nbuttons, page_dict = database_buttons()
    return render_template("intro.html",
                           webroot="http://"+request.host.replace(':5000',''),
                           page=page_dict,
                           obuttons=obuttons,
                           nbuttons=nbuttons)



#
#  - - - - - - - - - - P A G E S - - - - - - - - - -
#




class ErrorPage:
    """"""
    def __init__(self, error):
        """"""
        self.error = error

    def do_page(self, _a='', _b='', _c=''):
        """"""
        return self.not_found(self.error)

    def not_found(self, error):
        """"""
        print(error)
        obuttons, nbuttons, page_dict = database_buttons()
        resp = make_response(render_template('intro.html',
                                            error=error,
                                            webroot="http://"+request.host.replace(':5000',''),
                                            page=page_dict,
                                            obuttons=obuttons,
                                            nbuttons=nbuttons,
                                            ), 404)
        resp.headers['X-Something'] = 'A value'
        return resp

    def heading(self):
        """"""

    def set_thumb_size(self):
        """"""


def dbpage_factory(page, dbname):
    """factory for pages that use dbname"""
    dbpage_lookup = {'model'  : HtmlModelPage,
                     'models' : HtmlModelsPage,
                     'gallery': HtmlPhotoSetPage,
                     'photos' : HtmlPhotosPage,
                     'video'  : HtmlVideoPage,
                     'videos' : HtmlVideosPage,
                     'sites'  : HtmlSitesPage,
                     'site'   : HtmlSitePage,
                     'random' : HtmlRandomPage,
                     'rootpage' : HtmlRootPage,
                     'search' : HtmlSearchPage
                }

    try:
        return dbpage_lookup[page](dbname)
    except (InvalidDatabaseError,DatabaseMissingError):
        return ErrorPage(f"Not Found: Database [ {dbname} ] not found.") #ErrorPage(dbname)
    except KeyError:
        return ErrorPage(f"Not Found: Page [ {page} ] not found.") #ErrorPage(dbname)


def page_factory(page):
    """factory for root level pages with no dbname"""
    page_lookup = {'search' : HtmlSearchAll, # global search does not take dbname
                   'random' : HtmlRandomAll  # global random link generator
                  }
    try:
        return page_lookup[page]()
    except KeyError:
        return ErrorPage(f"Not Found: Page [ {page} ] not found.") #ErrorPage(dbname)


def file_system():
    try:
        #print("filesystem")
        return HtmlFileSystem()
    except:
        return ErrorPage("Not Found: Page [ fs ] not found.") #ErrorPage(dbname)
        #raise

#class ModelsPage:
#    def __init__(self, tagdicts, mtable):
#        self.table=mtable
#        self.tagdicts=tagdicts # member of HtmlSite class
#        self.name='models'
#        self.htmlfn='photos.html'
#        self.filter=''
#        self.filtid=''

#    def getitems(self, order):
#        order_by = {
#            'alpha':   'asc',   'ralpha':   'desc',
#            'vlatest': 'desc',  'rvlatest': 'asc',
#            'platest': 'desc',  'rplatest': 'asc',
#            'most':    'desc',  'least':    'asc',
#            'id':      'asc',   'rid':      'desc'
#        }
#        if order in ['alpha', 'ralpha']:
#            models = self.table.select_group_by_order_by('name', 'name', order_by[order])

#        elif order in ['vlatest', 'rvlatest']:
#            models = self.table.select_by_most_recent_videos('model_id', order_by[order])

#        elif order in ['platest', 'rplatest']:
#            models = self.table.select_by_most_recent_photos('model_id', order_by[order])

#        elif order in ['most', 'least']:
#            models = self.table.select_models_by_count(order_by[order])

#        elif order in ['id', 'rid']:
#            models = self.table.select_order_by('id', order_by[order])

#        if len(models) == 0:
#            models = self.table.select_order_by('id', 'desc')

#        return (models,)


#class ModelPage:
#    def __init__(self, tagdicts, modelid, dbt):
#        self.dbt=dbt
#        self.tagdicts=tagdicts
#        self.name='model'
#        self.modelid=modelid
#        self.filter='model'
#        self.filtid=modelid

#    def getitems(self, order):
#        order_by = {
#            'alpha': 'asc',  'ralpha': 'desc',
#            'id':    'asc',  'rid':    'desc',
#            'date':  'asc',  'rdate':  'desc'
#            }
#        unsorted_photos = self.dbt.photos_table().select_where_group_by('model_id',self.modelid,'id')
#        #    id, model_id, site_id, name, location, thumb, count, pdate = gallery
#        unsorted_videos = self.dbt.videos_table().select_where_group_by('model_id',self.modelid,'id')

#        # lambda is setting the database column to sort on - date is different between photos and videos
#        if order in ('alpha', 'ralpha'):
#            photos = sorted(unsorted_photos, key = lambda x: x[3]) #name
#            videos = sorted(unsorted_videos, key = lambda x: x[3])
#        elif order in ('id', 'rid'):
#            photos = sorted(unsorted_photos, key = lambda x: x[0]) # id
#            videos = sorted(unsorted_videos, key = lambda x: x[0])
#        elif order in ('date', 'rdate'):
#            photos = sorted(unsorted_photos, key = lambda x: x[7])  #pdate
#            videos = sorted(unsorted_videos, key = lambda x: x[10]) #vdate

#        if order_by[order] == 'desc':
#            photos.reverse()
#            videos.reverse()
#        return (photos, videos)


#class SitePage:
#    def __init__(self, tagdicts, siteid, dbt):
#        self.dbt=dbt
#        self.tagdicts=tagdicts
#        self.name='site'
#        self.siteid=siteid
#        self.filter='site'
#        self.filtid=siteid

#    def getitems(self, order):
#        sitename = self.dbt.sites_table().select_where('id', self.siteid)[0][1]
#        photos = self.dbt.photos_table().select_where_order_by('site_id', self.siteid, sorting[order][0], sorting[order][2])
#        videos = self.dbt.videos_table().select_where_order_by('site_id', self.siteid, vsorting[order][0], vsorting[order][2])
#        return (photos, videos)


#class SitesPage:
#    def __init__(self, tagdicts, stable):
#        self.table=stable
#        self.tagdicts=tagdicts
#        self.name='sites'
#        self.filter=''
#        self.filtid=''

#    def getitems(self, order):
#        order_by = {'most': 'desc', 'least': 'asc'}

#        if order in ['most', 'least']:
#            sites = self.table.select_sites_by_count(order_by[order])
#        else:
#            sites = self.table.select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
#        return (sites,)


#class VideosPage:
#    def __init__(self, tagdicts, vtable):
#        self.table=vtable
#        self.tagdicts=tagdicts
#        self.name='videos'
#        self.filter=''
#        self.filtid=''

#    def getitems(self, order):
#        items = self.table.select_order_by(vsorting[order][1], vsorting[order][2])
#        if len(items) == 0:
#            items = self.table.select_group_by_order_by('id', 'id', 'desc')
#        return (items,)


#class PhotosPage:
#    def __init__(self, tagdicts, ptable):
#        self.table=ptable
#        self.tagdicts=tagdicts
#        self.name='photos'
#        self.filter=''
#        self.filtid=''
#
#    def getitems(self, order):
#        items = self.table.select_order_by(sorting[order][1], sorting[order][2])
#        if len(items) == 0:
#            items = self.table.select_group_by_order_by('id', 'id', 'desc')
#        return (items,)

#class PageBuilder:
#    def __init__(self, page_data, htmlsiteclass):
#        self.page = page_data
#        self.htmlsite = htmlsiteclass

#    def build(self):
#        pgnum = get_page_num(1)
#        order = self.htmlsite.get_order(self.page.name)

#        items = self.page.getitems(order)

#        tagdicts = []
#        x=0
#        for tagdictfunc in self.page.tagdicts:
#            tagdicts.append(tagdictfunc(items[x], self.page.filtcol, self.page.filtid, pgnum))
#            x=x+1

#        links = self.htmlsite.heading(self.page.name)
#        page_dict = self.htmlsite.init_page_dict('',True,self.page.name,links)
#        page_dict['search'] = True
#        return page_dict, tagdicts
