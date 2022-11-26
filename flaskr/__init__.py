#!/usr/bin/env python3

"""
"""

from flask import Flask, request
#from flaskr.mark_I import *
from flaskr.mark_II import *

app = Flask(__name__)


class ErrorPage:
    def __init__(self, dbname):
        self.dbname = dbname

    def do(self, method, *args):
        """"""
        buttons, page_dict = databaseButtons()
        return render_template("error.html", 
                               webroot="http://gallery", #mysite.getConfig()['webroot'],
                               page=page_dict, 
                               buttons=buttons,
                               dbname=self.dbname
                               )
    def heading(self):
        pass

def createPage(dbname):
    """"""
    if os.path.exists(getDBpath(dbname)):
        return HtmlSite(dbname)
    else:
        return ErrorPage(dbname)


@app.route("/<dbname>/gallery/model/<mid>/<pid>")
def gallery_model(dbname, pid, mid):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('models')
    #return mysite.do_gallery(pid, 'model_id', mid, 'model', links)
    return mysite.do('do_gallery', pid, 'model_id', mid, 'model', links)

@app.route("/<dbname>/gallery/site/<sid>/<pid>")
def gallery_site(dbname, pid, sid):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('sites')
    #return mysite.do_gallery(pid, 'site_id', sid, 'site', links)
    return mysite.do('do_gallery', pid, 'site_id', sid, 'site', links)

@app.route("/<dbname>/gallery/<id>")
def gallery(dbname, id):
    """"""
    mysite = createPage(dbname)
    links = mysite.heading('photos')
    #return mysite.do_gallery(id, None, None, None, links)
    return mysite.do('do_gallery', id, None, None, None, links)


@app.route("/<dbname>/models")
def kindgirls_models(dbname):
    """"""
    mysite = createPage(dbname)
    #return mysite.models()
    return mysite.do('models')

@app.route("/<dbname>/model/<model>")
def kindgirls_model(dbname, model):
    """"""
    mysite = createPage(dbname)
    #return mysite.model(model)
    return mysite.do('model', model)


@app.route("/<dbname>/sites")
def kindgirls_sites(dbname):
    """"""
    mysite = createPage(dbname)
    #return mysite.sites()
    return mysite.do('sites')

@app.route("/<dbname>/site/<site>")
def kindgirls_site(dbname, site):
    """"""
    mysite = createPage(dbname)
    #return mysite.site(site)
    return mysite.do('site', site)


@app.route("/<dbname>/photos")
def photos(dbname):
    """"""
    mysite = createPage(dbname)
    #return mysite.photos()
    return mysite.do('photos')


@app.route("/<dbname>/videos")
def kindgirls_videos(dbname):
    """"""
    mysite = createPage(dbname)
    #return mysite.videos()
    return mysite.do('videos')


@app.route("/<dbname>/video/<vid>")
def kindgirls_video(dbname, vid):
    """"""
    mysite = createPage(dbname)
    #return mysite.video(vid, None, None)
    return mysite.do('video', vid, None, None)

@app.route("/<dbname>/video/site/<sid>/<vid>")
def kindgirls_video_site(dbname, vid, sid=None):
    """"""
    mysite = createPage(dbname)
    #return mysite.video(vid, sid)
    return mysite.do('video', vid, sid)

@app.route("/<dbname>/video/model/<mid>/<vid>")
def kindgirls_video_model(dbname, vid, sid=None, mid=None):
    """"""
    mysite = createPage(dbname)
    #return mysite.video(vid, sid, mid)
    return mysite.do('video', vid, sid, mid)


@app.route("/<dbname>/search", methods=['POST', 'GET'])
def search(dbname):
    """"""
    mysite = createPage(dbname)
    if request.method == 'GET':
        s = request.args.get('s')
    #return mysite.search(s)
    return mysite.do('search', s)

@app.route("/<dbname>/random")
def random(dbname):
    """"""
    mysite = createPage(dbname)
    return mysite.do('random')


@app.route("/<dbname>/edit/<table>/<id>")
def edit(dbname, table, id):
    """"""
    mysite = createPage(dbname)
    return mysite.do('edit', table, id)


@app.route("/<dbname>/")
@app.route("/<dbname>")
def kindgirls(dbname):
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8181)

