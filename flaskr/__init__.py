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
#from flaskr.mark_I import *
from flaskr.mark_II import *

app = Flask(__name__)
app.secret_key = "d76df0b23782624435e4e42b9fd79b99e1b1a1c387a145ecae02683d69cf2fda"

class ErrorPage:
    def __init__(self, error):
        self.error = error

    def do(self, method, *args):
        """"""
        return not_found(self.error)
        #buttons, page_dict = databaseButtons()
        #return render_template("error.html", 
        #                       webroot="http://gallery", #mysite.getConfig()['webroot'],
        #                       page=page_dict, 
        #                       buttons=buttons,
        #                       dbname=self.dbname
        #                       )
    def heading(self):
        pass

def createPage(dbname):
    """"""
    if os.path.exists(getDBpath(dbname)):
        return HtmlSite(dbname)
    else:
        return ErrorPage("Not Found: Database not found.") #ErrorPage(dbname)

def get_search_term():
    """"""
    if request.method == 'GET':
        s = request.args.get('s') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
    return s

def do_post_get():
    """"""
    if request.method == 'GET':
        s = request.args.get('s') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
        if s in ["large", "small", "inc", "dec"]:
            session['thumbsize'] = s
        o = request.args.get('o') # sort ( alpha/ralpha , latest/rlatest , pics/rpics)
        if o is not None:
            session['order'] = o
        print(f"session {session}")

@app.errorhandler(404)
def not_found(error):
    """"""
    print(error)
    buttons, page_dict = databaseButtons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         #webroot="http://gallery", #mysite.getConfig()['webroot'],
                                         page=page_dict, 
                                         buttons=buttons,
                                         ), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.route("/<dbname>/gallery/model/<mid>/<pid>")
def gallery_model(dbname, pid, mid):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('models')
    return mysite.do('do_gallery', pid, 'model_id', mid, 'model', links)

@app.route("/<dbname>/gallery/site/<sid>/<pid>")
def gallery_site(dbname, pid, sid):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('sites')
    return mysite.do('do_gallery', pid, 'site_id', sid, 'site', links)

@app.route("/<dbname>/gallery/<id>")
def gallery(dbname, id):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('photos')
    return mysite.do('do_gallery', id, None, None, None, links)


@app.route("/<dbname>/models", methods=['POST', 'GET'])
def models(dbname):
    """"""
    do_post_get()
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('models')

@app.route("/<dbname>/model/<model>")
def model(dbname, model):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('model', model)


@app.route("/<dbname>/sites")
def sites(dbname):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('sites')

@app.route("/<dbname>/site/<site>")
def site(dbname, site):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('site', site)

@app.route("/<dbname>/photos", methods=['POST', 'GET'])
def photos(dbname):
    """"""
    do_post_get()
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('photos')


@app.route("/<dbname>/videos", methods=['POST', 'GET'])
def videos(dbname):
    """"""
    do_post_get()
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('videos')


@app.route("/<dbname>/video/<vid>")
def video(dbname, vid):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, None, None)

@app.route("/<dbname>/video/site/<sid>/<vid>")
def video_site(dbname, vid, sid=None):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, sid)

@app.route("/<dbname>/video/model/<mid>/<vid>")
def video_model(dbname, vid, sid=None, mid=None):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('video', vid, sid, mid)


@app.route("/<dbname>/search", methods=['POST', 'GET'])
def search(dbname):
    """"""
    #do_get_post()
    term = get_search_term()
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('search', term)

@app.route("/<dbname>/random")
def random(dbname):
    """"""
    mysite = createPage(dbname)
    mysite.setThumbSize()
    return mysite.do('random')


@app.route("/<dbname>/edit/<table>/<id>")
def edit(dbname, table, id):
    """"""
    mysite = createPage(dbname)
    return mysite.do('edit', table, id)


@app.route("/<dbname>/")
@app.route("/<dbname>")
def dbroot(dbname):
    """"""
    mysite = createPage(dbname)
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

