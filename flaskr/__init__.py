#!/usr/bin/env python3

"""
"""

from flask import Flask
#from flaskr.mark_I import *
from flaskr.mark_II import *

app = Flask(__name__)


@app.route("/<dbname>/gallery/model/<mid>/<pid>")
def gallery_model(dbname, pid, mid):
    """"""
    mysite = HtmlSite(dbname)
    links = mysite.heading('models')
    return mysite.do_gallery(pid, 'model_id', mid, 'model', links)

@app.route("/<dbname>/gallery/site/<sid>/<pid>")
def gallery_site(dbname, pid, sid):
    """"""
    mysite = HtmlSite(dbname)
    links = mysite.heading('sites')
    return mysite.do_gallery(pid, 'site_id', sid, 'site', links)


@app.route("/<dbname>/gallery/<id>")
def gallery(dbname, id):
    """"""
    mysite = HtmlSite(dbname)
    links = mysite.heading('photos')
    return mysite.do_gallery(id, None, None, None, links)


@app.route("/<dbname>/models/<letter>")
@app.route("/<dbname>/models")
def kindgirls_models(dbname, letter=''):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.models(letter)


@app.route("/<dbname>/model/<model>/<letter>")
@app.route("/<dbname>/model/<model>")
def kindgirls_model(dbname, model, letter=''):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.model(model, letter)


@app.route("/<dbname>/sites")
def kindgirls_sites(dbname):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.sites()


@app.route("/<dbname>/site/<site>")
def kindgirls_site(dbname, site):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.site(site)


@app.route("/<dbname>/photos")
def photos(dbname):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.photos()


@app.route("/<dbname>/videos")
def kindgirls_videos(dbname):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.videos()


@app.route("/<dbname>/video/<vid>")
def kindgirls_video(dbname, vid):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.video(vid, None, None)

@app.route("/<dbname>/video/site/<sid>/<vid>")
def kindgirls_video_site(dbname, vid, sid=None):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.video(vid, sid)

@app.route("/<dbname>/video/model/<mid>/<vid>")
def kindgirls_video_model(dbname, vid, sid=None, mid=None):
    """"""
    mysite = HtmlSite(dbname)
    return mysite.video(vid, sid, mid)


@app.route("/<dbname>/")
@app.route("/<dbname>")
def kindgirls(dbname):
    """"""
    mysite = HtmlSite(dbname)
    buttons = [
        {'href':f"/{dbname}/photos", 'name':'Photos'},
        {'href':f"/{dbname}/models", 'name':'Models'},
        {'href':f"/{dbname}/sites",  'name':'Sites'},
        {'href':f"/{dbname}/videos", 'name':'Videos'},
    ]

    links = mysite.heading()
    page_dict = {'title':'', 'plaintitle':True, 'heading': mysite.config['title'], 'type':'', 'button_class':'fourbuttons'}
    return render_template("intro.html", 
                           page=page_dict,
                           buttons=buttons)


@app.route("/")
def index():
    """"""
    buttons = [{'href':'/kindgirls', 'name':'KindGirls'},
               {'href':'/inthecrack', 'name':'InTheCrack'}]

    page_dict = {'title':'Stuff', 'plaintitle':True, 'button_class':'twobuttons'}
    return render_template("intro.html", 
                           page=page_dict, 
                           buttons=buttons)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8181)

