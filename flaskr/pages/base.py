
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

import os
from flask import session, request, current_app

from flaskr.database.errors import DatabaseMissingError
from flaskr.database.utils import get_config, DatabaseTables
from flaskr.common.utils import human_time

def get_page_num(page):
    """"""
    if 'page' in session:
        page = session['page']
    return page


class PageInfo:
    def __init__(self, tagdicts, name, filtid=''):
        self.name = name
        self.tagdicts = tagdicts
        self.filtcol = '' if filtid=='' else name
        self.filtid = filtid


class PageBuilder:
    def __init__(self, info, htmlpageclass):
        self.info = info
        self.htmlpage = htmlpageclass

    def build(self):
        """self.info.name
           self.info.filtcol
           self.info.filtid
           self.info.tagdicts
        """
        pgnum = get_page_num(1)
        order = self.htmlpage.get_order(self.info.name)

        items = self.htmlpage.getitems(order)

        tagdicts = []
        x=0
        for tagdictfunc in self.info.tagdicts:
            tagdicts.append(tagdictfunc(items[x], self.info.filtcol, self.info.filtid, pgnum))
            x=x+1

        self.htmlpage.heading(self.info.name)
        page_dict = self.htmlpage.init_page_dict('', True, self.info.name) #, links)
        page_dict['search'] = True
        return page_dict, tagdicts


class HtmlSite:

    def __init__(self, dbname=''):
        """"""
        #error_occured = False
        self.dbname = dbname
        if dbname != '':
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                #error_occured = True
                raise
        else:
            self.db = None
            self.config = None
        self.pg = {'next':-1, 'prev':-1}
        self.links = {}

    def set_dbname(self, name):
        self.dbname = name

    def set_thumb_size(self):
        """"""
        if 'thumbsize' in session:
            if 'thumb_h' not in session:
                session['thumb_h'] = self.config['thumbsize']
            if session['thumbsize'] == "large":
                self.config['thumb_h'] = self.config['thumbsize']
            elif session['thumbsize'] == "small":
                self.config['thumb_h'] = self.config['thumbsize'] / 1.5


    def heading(self, page=None):
        """"""
        self.links = {
            "photos": {"href": f"/photos/{self.dbname}/", "title": "Photos", 'class':'', 'rows': self.db.photos_table().row_count() },
            "models": {"href": f"/models/{self.dbname}/", "title": "Girls",  'class':'', 'rows': self.db.models_table().row_count() },
            "sites":  {"href": f"/sites/{self.dbname}/",  "title": "Sites",  'class':'', 'rows':  self.db.sites_table().row_count()-1 },
            "videos": {"href": f"/videos/{self.dbname}/", "title": "Videos", 'class':'', 'rows': self.db.videos_table().row_count() }
            }

        if page is not None:
            if page == "site":
                page = "sites"
            if page == "model":
                page = "models"
            self.links[page]['class'] = " w3-dark-grey "

        #return links


    #def getConfig(self):
    #    """"""
    #    return self.config

    def get_order(self, page):
        """"""
        if 'order' in session:
            order = session['order']
        else:
            # get default from db
            sql = f"SELECT {page} FROM default_sort;"
            order = self.db.sort_table().get_single_result(sql,1)[0]

        return order



    def page_range(self, num, total, pgcount=0):
        """"""
        if pgcount == 0:
            pgcount = self.config['pgcount']
        self.pg = {'next': num+1 if (num * pgcount) < total else 0,
                   'prev': num-1 if (num - 1) > 0 else 0}
        current_app.logger.debug(f"{self.pg}")
        return (num-1)*pgcount, (num*pgcount)


    def moddict(self, models, _filtval='', _filtid='', pgnum=1):
        """"""
        cmodels = self.db.models_table().get_model_set_count()
        mdicts = []
        sidx, eidx = self.page_range(pgnum, len(models))
        for idx,name,thumb in models[sidx:eidx]:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href': f"/models/{self.dbname}/{idx}",
                           'src': thumburl,
                           'name': name,
                           'height': self.config['thumb_h'],
                           'count': cmodels[idx]}
                           )
        return mdicts


    def galdict(self, photos, filtval='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filtval != '':
            filterurl = f"/{filtval}/{filtid}"
        gdict = []
        sidx, eidx = self.page_range(pgnum, len(photos))
        for gallery in photos[sidx:eidx]:
            #idx, model_id, site_id, name, location, thumb, count, pdate = gallery
            idx, _, _, name, location, thumb, count, _ = gallery
            thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thumb}"
            #name = name.replace('_', ' ')[:50]
            gdict.append({'href': f"/photos/{self.dbname}/{filterurl}/{idx}",
                          'src': thumb,
                          'name': name.replace('_', ' ')[:50],
                          'height': self.config['thumb_h'],
                          'count': count,
                          'basename': os.path.basename(location)}
                          )
        return gdict


    def viddict(self, videos, filtval='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filtval != '':
            filterurl=f"/{filtval}/{filtid}"
        vdicts = []
        sidx, eidx = self.page_range(pgnum, len(videos), self.config['vpgcount'])
        for vid in videos[sidx:eidx]:
            #idx, model_id, site_id, name, filename, thumb, poster, width, height, length, vdate = vid
            idx, _, _, name, filename, thumb, _, width, height, length, _ = vid
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            vdicts.append({'href':f"/videos/{self.dbname}/{filterurl}/{idx}",
                           'src':thumb_url,
                           'name':name,
                           'theight':self.config['thumb_h'],
                           'w': width,
                           'h': height,
                           'mlen':human_time(length),
                           'basename': os.path.basename(filename)}
                           )
        return vdicts


    def sitdict(self, sites, _filtval='', _filtid='', pgnum=1):
        """"""
        #sites_count = {}
        csites = self.db.sites_table().get_sites_set_count()
        ordered_sites = {}
        sdict = []
        sidx, eidx = self.page_range(pgnum, len(sites))
        for idx,name,_location in sites[sidx:eidx]:
            try:
                pid,_,_,_,_,thm = self.db.photos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][:6]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/sites/{self.dbname}/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/sites/{self.dbname}/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
            except IndexError:
                vname = self.db.videos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/sites/{self.dbname}/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/sites/{self.dbname}/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
        return sdict


    def init_page_dict(self, title, plaintitle, ptype):
        """"""
        return {
            'title':title, 'db':self.dbname, 'heading':self.config['title'],
            'plaintitle':plaintitle, 'navigation':self.links, 'type':ptype, 'pg':self.pg,
            'url': request.base_url
        }

    def search_all_tables(self, term):
        """"""
        sites = self.db.sites_table().select_where_like('name', term)
        models = self.db.models_table().select_where_like('name', term)
        photos = self.db.photos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc')
        videos = self.db.videos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc')

        modeldicts = self.moddict(models)
        galldicts = self.galdict(photos)
        viddicts = self.viddict(videos)
        sitedicts = self.sitdict(sites)

        return modeldicts, galldicts, viddicts, sitedicts


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



