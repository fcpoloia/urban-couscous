#!/usr/bin/env python3

# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

"""
# init module for flaskr webapp

<dbname>      -  kindgirls/hegreart/femjoy/alsangels/inthecrack/alsscans
<listpage>    -  photos/models/sites/videos
<singlepage>  -  gallery/video/model
<filter>      -  site/model (works with video and gallery page)
<otherpages>  -  random/search
<option>      -  x2thumbsize
<sort>        -  alpha/latest/most/piccount


/<dbname>/<page><id>/<filter><id>/<option>/<sort>
thumbsize x2
sort order(alpha,latest,most,pics)

@app.route("/favicon.ico")
@app.route("/")

# new layout to implement

/models/<db>/
/models/<db>/<id>
/sites/<db>/
/sites/<db>/<id>
/videos/<db>/
/videos/<db>/<id>
/photos/<db>/
/photos/<db>/<id>

/photos/<db>/model/<mid>/<pid>
/photos/<db>/site/<sid>/<pid>
/videos/<db>/model/<mid>/<pid>
/videos/<db>/site/<sid>/<pid>

/random/<db>
/search/<db>

/random
/search

"""

from logging.config import dictConfig
from markupsafe import escape
from flask import Flask, request, make_response, current_app
from flask.views import View

from flaskr.factory import database_buttons, render_template, site_root

from flaskr.database.errors import DatabaseMissingError

from flaskr.pages.base import do_post_get
from flaskr.pages.fs import FileSystemView
from flaskr.pages.video import VideoPageView, HtmlVideoPage #, HtmlVideosPage
#from flaskr.pages.model import HtmlModelsPage, HtmlModelPage
from flaskr.pages.photo import GalleryIdxPageView, GalleryPageView #, HtmlPhotosPage
#from flaskr.pages.site import HtmlSitesPage, HtmlSitePage
from flaskr.pages.common import DBSearchPageView, DBRandomPageView, RandomPageView, SearchPageView


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.secret_key = "d76df0b23782624435e4e42b9fd79b99e1b1a1c387a145ecae02683d69cf2fda"


@app.errorhandler(404)
def not_found(error):
    """"""
    print(error)
    _obuttons, _nbuttons, page_dict = database_buttons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         webroot="http://"+request.host.replace(':5000',''),
                                         page=page_dict,
                                         ), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


@app.errorhandler(DatabaseMissingError)
def DatabaseError(error):
    """"""
    print(error)
    _obuttons, _nbuttons, page_dict = database_buttons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         webroot="http://"+request.host.replace(':5000',''),
                                         page=page_dict,
                                         ), 500)
    resp.headers['X-Something'] = 'A value'
    return resp





# --------------------gallery page id id-------------------------------

app.add_url_rule("/photos/<dbname>/<page>/<pageid>/<photoid>", view_func=GalleryPageView.as_view("gallery_page"))
app.add_url_rule("/photos/<dbname>/<idx>", view_func=GalleryIdxPageView.as_view("gallery_idx_page"))

# ---------------------page--------------------------------------------

#@app.route("/<dbname>/models", methods=['POST', 'GET'])
#@app.route("/<dbname>/sites", methods=['POST', 'GET'])
#@app.route("/<dbname>/photos", methods=['POST', 'GET'])
#@app.route("/<dbname>/videos", methods=['POST', 'GET'])
#@app.route("/<dbname>/<page>", methods=['POST', 'GET'])


#class DBPageView(View):
#    """"""
#    def __init__(self, htmlpage):
#        """"""
#        self.htmlpage = htmlpage
        #current_app.logger.info(f"DBPageView - methods: {self.name}")

#    def dispatch_request(self, dbname):
#        """"""
#        do_post_get()
#        mysite = self.htmlpage(dbname)
#        mysite.set_thumb_size()
#        return mysite.do_page()

#app.add_url_rule("/models/<dbname>/", view_func=DBPageView.as_view("models_page", HtmlModelsPage))
#app.add_url_rule("/sites/<dbname>/",  view_func=DBPageView.as_view("sites_page",  HtmlSitesPage))
#app.add_url_rule("/photos/<dbname>/", view_func=DBPageView.as_view("photos_page", HtmlPhotosPage))
#app.add_url_rule("/videos/<dbname>/", view_func=DBPageView.as_view("videos_page", HtmlVideosPage))

# ---------------------page id-----------------------------------------

#@app.route("/<dbname>/model/<modelid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/site/<siteid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/video/<vid>")
#@app.route("/<dbname>/<page>/<index>", methods=['POST', 'GET'])


class DBPageIdView(View):
    """"""
    def __init__(self, htmlpage):
        """"""
        self.htmlpage = htmlpage

    def dispatch_request(self, dbname, index):
        """"""
        do_post_get()
        mysite = self.htmlpage(dbname)
        mysite.set_thumb_size()
        return mysite.do_page(index)


#app.add_url_rule("/models/<dbname>/<index>", view_func=DBPageIdView.as_view("modelid_page", HtmlModelPage))
#app.add_url_rule("/sites/<dbname>/<index>",  view_func=DBPageIdView.as_view("siteid_page",  HtmlSitePage))
app.add_url_rule("/videos/<dbname>/<index>", view_func=DBPageIdView.as_view("videoid_page", HtmlVideoPage))


app.add_url_rule("/videos/<dbname>/<page>/<pageid>/<vid>", view_func=VideoPageView.as_view("video_page"))

app.add_url_rule("/search/<dbname>/", view_func=DBSearchPageView.as_view("searchdb_page"))
app.add_url_rule("/random/<dbname>/", view_func=DBRandomPageView.as_view("randomdb_page"))
app.add_url_rule("/random", view_func=RandomPageView.as_view("random_page"))
app.add_url_rule("/search", view_func=SearchPageView.as_view("search_page"))

app.add_url_rule("/fs/<path:subpath>", view_func=FileSystemView.as_view("fs_path"))
app.add_url_rule("/fs", view_func=FileSystemView.as_view("fs_root"))
app.add_url_rule("/fs/", view_func=FileSystemView.as_view("fs_root_slash"))

# new site page for testing
from flaskr.newsite import DBNewSiteView, DBNewSiteIdView

app.add_url_rule("/sites/<dbname>/",          view_func=DBNewSiteView.as_view("new_sites_page", 'sites')) # list of sites
app.add_url_rule("/models/<dbname>/",         view_func=DBNewSiteView.as_view("new_models_page", 'models')) # list of models
app.add_url_rule("/photos/<dbname>/",         view_func=DBNewSiteView.as_view("new_photos_page", 'photos')) # list of photos
app.add_url_rule("/videos/<dbname>/",         view_func=DBNewSiteView.as_view("new_videos_page", 'videos')) # list of videos

app.add_url_rule("/sites/<dbname>/<index>",   view_func=DBNewSiteIdView.as_view("new_siteid_page",  'site')) # list of photosets and videos for a site_id
app.add_url_rule("/models/<dbname>/<index>",  view_func=DBNewSiteIdView.as_view("new_modelid_page", 'model')) # list of photosets and videos for a model_id

#app.add_url_rule("/photos/<dbname>/<index>",  view_func=DBNewSiteIdView.as_view("new_photoid_page", 'photo')) # this is a gallery page
#app.add_url_rule("/videos/<dbname>/<index>",  view_func=DBNewSiteIdView.as_view("new_videoid_page", 'video')) # this is a single video


@app.route("/favicon.ico")
@app.route("/android-chrome-512x512.png")
@app.route("/android-chrome-192x192.png")
def favicon():
    """"""
    app.logger.debug("favicon.ico handled")
    return ""


@app.route("/")
def site_index():
    """"""
    return site_root()


# ----  testing ----

class Testing(View):
    """"""
    def __init__(self):
        """"""

    def dispatch_request(self, subpath):
        """"""
        #users = User.query.all()
        app.logger.info("arse")
        return f'Subpath {escape(subpath)}' #render_template("users.html", objects=users)

app.add_url_rule("/path/<path:subpath>", view_func=Testing.as_view("user_list"))

# ----------------main-------------------------------------------------

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8181)



