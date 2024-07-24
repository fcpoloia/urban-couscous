#!/usr/bin/env python3

# pylint: disable-msg=empty-docstring

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


@app.route("/<dbname>/gallery/model/<mid>/<pid>")
@app.route("/<dbname>/gallery/site/<sid>/<pid>")
@app.route("/<dbname>/gallery/<id>")
@app.route("/<dbname>/models", methods=['POST', 'GET'])
@app.route("/<dbname>/model/<model>")
@app.route("/<dbname>/sites")
@app.route("/<dbname>/site/<site>", methods=['POST, 'GET'])
@app.route("/<dbname>/photos", methods=['POST', 'GET'])
@app.route("/<dbname>/videos", methods=['POST', 'GET'])
@app.route("/<dbname>/video/<vid>")
@app.route("/<dbname>/video/site/<sid>/<vid>")
@app.route("/<dbname>/video/model/<mid>/<vid>")
@app.route("/<dbname>/search", methods=['POST', 'GET'])
@app.route("/<dbname>/random")
@app.route("/<dbname>/edit/<table>/<id>")
@app.route("/<dbname>/")
@app.route("/<dbname>")
@app.route("/favicon.ico")
@app.route("/")
"""

from markupsafe import escape
from flask import Flask, request, session, make_response
from flaskr.factory import database_buttons, render_template, site_root, dbpage_factory, page_factory, file_system
from flaskr.database.errors import DatabaseMissingError


app = Flask(__name__)
app.secret_key = "d76df0b23782624435e4e42b9fd79b99e1b1a1c387a145ecae02683d69cf2fda"

@app.errorhandler(404)
def not_found(error):
    """"""
    print(error)
    obuttons, nbuttons, page_dict = database_buttons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         webroot="http://"+request.host.replace(':5000',''),
                                         page=page_dict,
                                         obuttons=obuttons,
                                         nbuttons=nbuttons,
                                         ), 404)
    resp.headers['X-Something'] = 'A value'
    return resp



def get_search_term():
    """"""
    s = None
    if request.method == 'GET':
        s = request.args.get('search') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
    return s

def do_post_get():
    """"""
    print(f"{request.url}")
    if request.method == 'GET':
        if len(request.query_string) == 0:
            if 'order' in session:
                del session['order']
            if 'page' in session:
                del session['page']
        else:
            print(f"request query = {request.query_string}")

            s = request.args.get('size')
            if s in ["large", "small", "inc", "dec"]:
                session['thumbsize'] = s

            i = request.args.get('image')
            if i in ["large", "medium", "small", "thumb"]:
                session['imagesize'] = i

            o = request.args.get('order') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
            if o is not None:
                session['order'] = o

            p = request.args.get('page')
            if p is not None:
                try:
                    session['page'] = int(p)
                except ValueError:
                    pass # not a value page number

        #print(f"session {session}")
    else:
        print("not a get method")


# --------------------gallery page id id-------------------------------

#@app.route("/<dbname>/gallery/site/<sid>/<pid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/gallery/model/<mid>/<pid>", methods=['POST', 'GET'])
@app.route("/<dbname>/gallery/<page>/<pageid>/<photoid>", methods=['POST', 'GET'])
def gallery_page_id_id(dbname, page, pageid, photoid):
    """"""
    do_post_get()
    print(f"route gallery_page_id_id {photoid}")
    mysite = dbpage_factory('gallery',dbname)
    links = mysite.heading(page+'s')
    return mysite.do_gallery(photoid, page+'_id', pageid, page, links)

@app.route("/<dbname>/gallery/<idx>", methods=['POST', 'GET'])
def gallery(dbname, idx):
    """"""
    do_post_get()
    print(f"route dbname gallery {idx}")
    mysite = dbpage_factory('gallery',dbname)
    links = mysite.heading('photos')
    return mysite.do_gallery(idx, None, None, None, links)


# ---------------------page--------------------------------------------

#@app.route("/<dbname>/models", methods=['POST', 'GET'])
#@app.route("/<dbname>/sites", methods=['POST', 'GET'])
#@app.route("/<dbname>/photos", methods=['POST', 'GET'])
#@app.route("/<dbname>/videos", methods=['POST', 'GET'])
@app.route("/<dbname>/<page>", methods=['POST', 'GET'])
def dbname_page(dbname, page):
    """"""
    do_post_get()
    mysite = dbpage_factory(page,dbname)
    mysite.set_thumb_size()
    return mysite.do_page()


# ---------------------page id-----------------------------------------

#@app.route("/<dbname>/model/<modelid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/site/<siteid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/video/<vid>")
@app.route("/<dbname>/<page>/<index>", methods=['POST', 'GET'])
def dbname_page_id(dbname, page, index):
    """"""
    do_post_get()
    mysite = dbpage_factory(page,dbname)
    mysite.set_thumb_size()
    return mysite.do_page(index)


# --------------------video page id id --------------------------------

#@app.route("/<dbname>/video/site/<sid>/<vid>")
#@app.route("/<dbname>/video/model/<mid>/<vid>")
@app.route("/<dbname>/video/<page>/<pageid>/<vid>")
def video_page_id_id(dbname, page, pageid, vid=None):
    """"""
    mysite = dbpage_factory('video',dbname)
    mysite.set_thumb_size()
    return mysite.do_page(vid, page, pageid)

# ----------------miscellaneous----------------------------------------

@app.route("/<dbname>/search", methods=['POST', 'GET'])
def search(dbname):
    """"""
    term = get_search_term()
    mysite = dbpage_factory('search',dbname)
    mysite.set_thumb_size()
    return mysite.search(term)

@app.route("/<dbname>/random")
def random(dbname):
    """"""
    mysite = dbpage_factory('random',dbname) #HtmlRandom(dbname)
    mysite.set_thumb_size()
    return mysite.random()


@app.route("/<dbname>/")
@app.route("/<dbname>")
def dbroot(dbname):
    """"""
    mysite = dbpage_factory('rootpage',dbname) #HtmlRootPage(dbname)
    return mysite.rootpage()


@app.route("/search", methods=['POST', 'GET'])
def search_all():
    """global search page"""
    term = get_search_term()
    mysite = page_factory('search') #HtmlSearchAll()
    return mysite.search(term)


@app.route("/random")
def random_all():
    """global random page"""
    mysite = page_factory('random') #HtmlRandomAll()
    return mysite.random()


@app.route("/fs/<path:subpath>")
@app.route("/fs")
def filesystem(subpath='/'):
    """navigate the filesystem rather than databases"""
    mysite = file_system()
    return mysite.fs(subpath)


@app.route("/favicon.ico")
def favicon():
    """"""
    print("favicon.ico handled")
    return ""


@app.route("/")
def site_index():
    """"""
    return site_root()

# ----  testing ----

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    """"""
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'


# ----------------main-------------------------------------------------

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8181)


# ----------------obsoleted methods------------------------------------

#@app.route("/<dbname>/edit/<table>/<idx>")
#def edit(dbname, table, idx):
#    """"""
#    mysite = page_factory(dbname)
#    return mysite.do('edit', table, idx)


#@app.route("/<dbname>/gallery/model/<mid>/<pid>", methods=['POST', 'GET'])
#def gallery_model(dbname, pid, mid):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('gallery',dbname)
#    links = mysite.heading('models')
#    return mysite.do('do_gallery', pid, 'model_id', mid, 'model', links)

#@app.route("/<dbname>/gallery/site/<sid>/<pid>", methods=['POST', 'GET'])
#def gallery_site(dbname, pid, sid):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('gallery',dbname)
#    links = mysite.heading('sites')
#    return mysite.do('do_gallery', pid, 'site_id', sid, 'site', links)

#@app.route("/<dbname>/video/site/<sid>/<vid>")
#def video_site(dbname, vid, sid=None):
#    """"""
#    mysite = dbpage_factory('video',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('video', vid, sid)

#@app.route("/<dbname>/video/model/<mid>/<vid>")
#def video_model(dbname, vid, sid=None, mid=None):
#    """"""
#    mysite = dbpage_factory('video',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('video', vid, sid, mid)

#@app.route("/<dbname>/models", methods=['POST', 'GET'])
#def models(dbname):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('models',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('models')

#@app.route("/<dbname>/model/<modelid>", methods=['POST', 'GET'])
#def model(dbname, modelid):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('model',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('model', modelid)


#@app.route("/<dbname>/sites", methods=['POST', 'GET'])
#def sites(dbname):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('sites',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('sites')

#@app.route("/<dbname>/site/<siteid>", methods=['POST', 'GET'])
#def site(dbname, siteid):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('site',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('site', siteid)

#@app.route("/<dbname>/photos", methods=['POST', 'GET'])
#def photos(dbname):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('photos',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('photos')


#@app.route("/<dbname>/videos", methods=['POST', 'GET'])
#def videos(dbname):
#    """"""
#    do_post_get()
#    mysite = dbpage_factory('videos',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('videos')


#@app.route("/<dbname>/video/<vid>")
#def video(dbname, vid):
#    """"""
#    mysite = dbpage_factory('video',dbname)
#    mysite.set_thumb_size()
#    return mysite.do('video', vid, None, None)
