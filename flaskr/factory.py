#!/usr/bin/env python3

# pylint: disable-msg=line-too-long
# pylint: disable-msg=empty-docstring
# pylint: disable-msg=missing-class-docstring,missing-function-docstring
# pylint: disable-msg=unused-variable

"""
# Mark II verion of the website using a different database schema
"""

from flask import request, render_template, make_response

#from flaskr.database.errors import DatabaseMissingError, InvalidDatabaseError
from flaskr.database.utils import database_buttons

#from flaskr.pages.photo import HtmlPhotoSetPage #, HtmlPhotosPage
#from flaskr.pages.video import HtmlVideoPage #, HtmlVideosPage
#from flaskr.pages.model import HtmlModelsPage, HtmlModelPage
#from flaskr.pages.site  import HtmlSitesPage,  HtmlSitePage
#from flaskr.pages.common import HtmlSearchPage, HtmlRandomPage, HtmlRootPage


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


# class ErrorPage:
#     """"""
#     def __init__(self, error):
#         """"""
#         self.error = error

#     def do_page(self, _a='', _b='', _c=''):
#         """"""
#         return self.not_found(self.error)

#     def not_found(self, error):
#         """"""
#         print(error)
#         _obuttons, _nbuttons, page_dict = database_buttons()
#         resp = make_response(render_template('intro.html',
#                                             error=error,
#                                             webroot="http://"+request.host.replace(':5000',''),
#                                             page=page_dict,
#                                             ), 404)
#         resp.headers['X-Something'] = 'A value'
#         return resp

#     def heading(self):
#         """"""

#     def set_thumb_size(self):
#         """"""

#     def rootpage(self):
#         """"""
#         self.not_found("shouldn't be getting here!")


# def dbpage_factory(page, dbname):
#     """factory for pages that use dbname"""
#     dbpage_lookup = {#'model'  : HtmlModelPage,
#                      #'models' : HtmlModelsPage,
#                      'gallery': HtmlPhotoSetPage,
#                      #'photos' : HtmlPhotosPage,
#                      #'video'  : HtmlVideoPage,
#                      #'videos' : HtmlVideosPage,
#                      #'sites'  : HtmlSitesPage,
#                      #'site'   : HtmlSitePage,
#                      'random' : HtmlRandomPage,
#                      'rootpage' : HtmlRootPage,
#                      'search' : HtmlSearchPage
#                 }

#     try:
#         return dbpage_lookup[page](dbname)
#     except (InvalidDatabaseError,DatabaseMissingError):
#         return ErrorPage(f"Not Found: Database [ {dbname} ] not found.") #ErrorPage(dbname)
#     except KeyError:
#         return ErrorPage(f"Not Found: Page [ {page} ] not found.") #ErrorPage(dbname)


#def page_factory(page):
#    """factory for root level pages with no dbname"""
#    page_lookup = {'search' : HtmlSearchAll, # global search does not take dbname
#                   'random' : HtmlRandomAll  # global random link generator
#                  }
#    try:
#        return page_lookup[page]()
#    except KeyError:
#        return ErrorPage(f"Not Found: Page [ {page} ] not found.") #ErrorPage(dbname)



