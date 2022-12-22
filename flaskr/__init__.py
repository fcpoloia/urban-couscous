#!/usr/bin/env python3

"""
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

"""


"""
@app.route("/<dbname>/gallery/model/<mid>/<pid>")
@app.route("/<dbname>/gallery/site/<sid>/<pid>")
@app.route("/<dbname>/gallery/<id>")
@app.route("/<dbname>/models", methods=['POST', 'GET'])
@app.route("/<dbname>/model/<model>")
@app.route("/<dbname>/sites")
@app.route("/<dbname>/site/<site>")
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

from flask import Flask, request, session, make_response
#from .mark_I import *
from .mark_II import *

app = Flask(__name__)
app.secret_key = "d76df0b23782624435e4e42b9fd79b99e1b1a1c387a145ecae02683d69cf2fda"

@app.errorhandler(404)
def not_found(error):
    """"""
    print(error)
    buttons, page_dict = databaseButtons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         page=page_dict, 
                                         buttons=buttons,
                                         ), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

class ErrorPage:
    def __init__(self, error):
        self.error = error

    def do(self, method, *args):
        """"""
        return not_found(self.error)

    def heading(self):
        pass

def page_factory(dbname):
    """"""
    if os.path.exists(getDBpath(dbname)):
        return HtmlSite(dbname)
    else:
        return ErrorPage("Not Found: Database not found.") #ErrorPage(dbname)

def get_search_term():
    """"""
    if request.method == 'GET':
        s = request.args.get('search') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
    return s

def do_post_get():
    """"""
    print(f"{request.url}")
    if request.method == 'GET':
        if len(request.query_string) == 0:
            if 'order' in session: del session['order']
            if 'page' in session: del session['page']
        else:
            print(f"request query = {request.query_string}")
        
            s = request.args.get('size')
            if s in ["large", "small", "inc", "dec"]:
                session['thumbsize'] = s

            i = request.args.get('image')
            if i in ["large", "small"]:
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
        print(f"not a get method")

@app.route("/<dbname>/gallery/model/<mid>/<pid>", methods=['POST', 'GET'])
def gallery_model(dbname, pid, mid):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    links = mysite.heading('models')
    return mysite.do('do_gallery', pid, 'model_id', mid, 'model', links)

@app.route("/<dbname>/gallery/site/<sid>/<pid>", methods=['POST', 'GET'])
def gallery_site(dbname, pid, sid):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    links = mysite.heading('sites')
    return mysite.do('do_gallery', pid, 'site_id', sid, 'site', links)

@app.route("/<dbname>/gallery/<id>", methods=['POST', 'GET'])
def gallery(dbname, id):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    links = mysite.heading('photos')
    return mysite.do('do_gallery', id, None, None, None, links)


@app.route("/<dbname>/models", methods=['POST', 'GET'])
def models(dbname):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('models')

@app.route("/<dbname>/model/<model>")
def model(dbname, model):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('model', model)


@app.route("/<dbname>/sites", methods=['POST', 'GET'])
def sites(dbname):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('sites')

@app.route("/<dbname>/site/<site>")
def site(dbname, site):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('site', site)

@app.route("/<dbname>/photos", methods=['POST', 'GET'])
def photos(dbname):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('photos')


@app.route("/<dbname>/videos", methods=['POST', 'GET'])
def videos(dbname):
    """"""
    do_post_get()
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('videos')


@app.route("/<dbname>/video/<vid>")
def video(dbname, vid):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, None, None)

@app.route("/<dbname>/video/site/<sid>/<vid>")
def video_site(dbname, vid, sid=None):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, sid)

@app.route("/<dbname>/video/model/<mid>/<vid>")
def video_model(dbname, vid, sid=None, mid=None):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, sid, mid)


@app.route("/<dbname>/search", methods=['POST', 'GET'])
def search(dbname):
    """"""
    #do_post_get()
    term = get_search_term()
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('search', term)

@app.route("/<dbname>/random")
def random(dbname):
    """"""
    mysite = page_factory(dbname)
    mysite.setThumbSize()
    return mysite.do('random')


@app.route("/<dbname>/edit/<table>/<id>")
def edit(dbname, table, id):
    """"""
    mysite = page_factory(dbname)
    return mysite.do('edit', table, id)


@app.route("/<dbname>/")
@app.route("/<dbname>")
def dbroot(dbname):
    """"""
    mysite = page_factory(dbname)
    return mysite.do('rootpage')

@app.route("/favicon.ico")
def favicon():
    """"""
    print("favicon.ico handled")
    return ""

@app.route("/")
def index():
    return siteRoot()

# ----  testing ----
from markupsafe import escape

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8181)

