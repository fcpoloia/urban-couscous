#!/usr/bin/env python3

# pylint: disable-msg=line-too-long
# pylint: disable-msg=empty-docstring
# pylint: disable-msg=missing-class-docstring,missing-function-docstring
# pylint: disable-msg=unused-variable

"""
# Mark II verion of the website using a different database schema
"""

import glob
import os
import sys
import random
from subprocess import getstatusoutput as unix
from flask import request, render_template, session, make_response
from .db2 import ConfigTable, SortTable, ModelsTable, SitesTable, PhotosTable, VideosTable, DatabaseMissingError


sorting = {
    'alpha':  ['name','name','asc'],
    'ralpha': ['name','name','desc'],
    'pics':   ['id','count','desc'],
    'rpics':  ['id','count','asc'],
    'id':     ['id','id','asc'],
    'rid':    ['id','id','desc'],
    'date':   ['pdate','pdate','asc'],
    'rdate':  ['pdate','pdate','desc']
}
vsorting = {
    'alpha':  ['name','name','asc'],
    'ralpha': ['name','name','desc'],
    'pics':   ['id','count','desc'],
    'rpics':  ['id','count','asc'],
    'id':     ['id','id','asc'],
    'rid':    ['id','id','desc'],
    'date':   ['vdate','vdate','asc'],
    'rdate':  ['vdate','vdate','desc']
}


class InvalidDatabaseError(Exception):
    """custom exception"""
    #pass




def database_buttons():
    """"""
    sql = "SELECT title FROM config;"
    obuttons = []
    nbuttons = []
    names = []
    dblist = {}
    for database in glob.glob("flaskr/old_*.db"):
        dbname = database.replace('flaskr/old_','').replace('.db','')
        name = ConfigTable(database).get_single_result(sql,1)[0]
        dblist[dbname] = name
        names.append(dbname)
    names.sort()
    for dbname in names:
        obuttons.append({'href':'/'+dbname, 'name':dblist[dbname]})

    names = []
    for database in glob.glob("flaskr/new_*.db"):
        dbname = database.replace("flaskr/new_",'').replace('.db','')
        name = ConfigTable(database).get_single_result(sql,1)[0]
        dblist[dbname] = name
        names.append(dbname)
    names.sort()
    for dbname in names:
        nbuttons.append({'href':'/'+dbname, 'name':dblist[dbname]})


    page_dict = {
        'title':'',
        'heading':'Stuff',
        'plaintitle':True,
        'button_class':'fivebuttons'
    }
    return obuttons, nbuttons, page_dict


def random_selection(datalist, count):
    """"""
    if len(datalist) <= 1:
        return datalist

    selection = []
    nums = []

    while len(selection) < count:
        num = random.randrange(len(datalist))
        if num not in nums:
            nums.append(num)
            selection.append(datalist[num])
    return selection


def site_root():
    """"""
    obuttons, nbuttons, page_dict = database_buttons()
    return render_template("intro.html",
                           webroot="http://"+request.host.replace(':5000',''),
                           page=page_dict,
                           obuttons=obuttons,
                           nbuttons=nbuttons)


def get_page_num(page):
    """"""
    if 'page' in session:
        page = session['page']
    return page


def human_time(length):
    """take seconds input and return time in hours:mins:secs"""
    if length is None:
        return ""
    if length > 3600.0:
        hours = int(length/3600)
        mins = int((length-(hours*3600))/60)
        secs = int(length-(hours*3600)-(mins*60))
        return f"{hours}:{mins:02d}:{secs:02d}"
    if length > 60.0:
        mins = int(length/60)
        secs = int(length-(mins*60))
        return f"{mins}:{secs:02d}"
    return f"{int(length)}"


class Database:
    def __init__(self, dbname):
        """"""
        self.dbname = dbname
        self._dbpath = self.get_db_path()

    def get_db_path(self):
        """"""
        old = f"flaskr/old_{self.dbname}.db"
        new = f"flaskr/new_{self.dbname}.db"
        path = ""
        if os.path.exists(old):
            path = old
        if os.path.exists(new):
            path = new
        return path

    @property
    def dbpath(self):
        return self._dbpath

    @dbpath.setter
    def dbpath(self, path):
        self._dbpath = path


class DatabaseTables:
    """"""
    def __init__(self, dbname):
        """"""
        self.db = Database(dbname)

    def models_table(self):
        return ModelsTable(self.db.dbpath)

    def photos_table(self):
        return PhotosTable(self.db.dbpath)

    def videos_table(self):
        return VideosTable(self.db.dbpath)

    def sites_table(self):
        return SitesTable(self.db.dbpath)

    def config_table(self):
        return ConfigTable(self.db.dbpath)

    def sort_table(self):
        return SortTable(self.db.dbpath)


def get_config(dbname):
    """Read Config Table"""
    dbt = DatabaseTables(dbname)
    try:
        vals = dbt.config_table().select_all()[0]
        cols = dbt.config_table().column_list()
        config = {}
        if len(vals) == len(cols):
            for i, col in enumerate(cols): #range(len(cols)):
                config[col] = vals[i]
        #print(config)
    except DatabaseMissingError:
        raise
    # fix the webroot so that it copes with both name or ip provided in url
    config['webroot'] = "http://"+request.host.replace(':5000','')
    # append more items
    config['thumbsize'] = 240
    config['thumb_h'] = 240
    config['pgcount'] = 500
    config['vpgcount'] = 100

    return config


class HtmlSite:

    def __init__(self, dbname=''):
        """"""
        error_occured = False
        self.dbname = dbname
        if dbname != '':
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                error_occured = True
                raise
        else:
            self.db = None
            self.config = None
        self.pg = {'next':-1, 'prev':-1}

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
        links = {
            "photos": {"href": f"/{self.dbname}/photos", "title": "Photos", 'class':'', 'rows': self.db.photos_table().row_count() },
            "models": {"href": f"/{self.dbname}/models", "title": "Girls",  'class':'', 'rows': self.db.models_table().row_count() },
            "sites":  {"href": f"/{self.dbname}/sites",  "title": "Sites",  'class':'', 'rows':  self.db.sites_table().row_count()-1 },
            "videos": {"href": f"/{self.dbname}/videos", "title": "Videos", 'class':'', 'rows': self.db.videos_table().row_count() }
            }

        if page is not None:
            if page == "site":
                page = "sites"
            if page == "model":
                page = "models"
            links[page]['class'] = " w3-dark-grey "

        return links


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
        return (num-1)*pgcount, (num*pgcount)


    def moddict(self, models, _filtval='', _filtid='', pgnum=1):
        """"""
        cmodels = self.db.models_table().get_model_set_count()
        mdicts = []
        sidx, eidx = self.page_range(pgnum, len(models))
        for idx,name,thumb in models[sidx:eidx]:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href': f"/{self.dbname}/model/{idx}",
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
            gdict.append({'href': f"/{self.dbname}/gallery{filterurl}/{idx}",
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
            vdicts.append({'href':f"/{self.dbname}/video{filterurl}/{idx}",
                           'src':thumb_url,
                           'name':name,
                           'theight':self.config['thumb_h'],
                           'w': width,
                           'h': height,
                           'mlen':human_time(length),
                           'basename': os.path.basename(filename)}
                           )
        return vdicts


    def sitdict(self, sites, _filtval='', _filtid='', _pgnum=1):
        """"""
        sites_count = {}
        csites = self.db.sites_table().get_sites_set_count()
        ordered_sites = {}
        sdict = []
        for idx,name,location in sites:
            try:
                pid,_,_,_,_,thm = self.db.photos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][:6]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/{self.dbname}/site/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/{self.dbname}/site/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
            except IndexError:
                vname = self.db.videos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/{self.dbname}/site/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/{self.dbname}/site/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
        return sdict


    def init_page_dict(self, title, plaintitle, ptype, links):
        """"""
        return {
            'title':title, 'db':self.dbname, 'heading':self.config['title'],
            'plaintitle':plaintitle, 'navigation':links, 'type':ptype, 'pg':self.pg,
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

#
#  - - - - - - - - - - P A G E S - - - - - - - - - -
#

class HtmlSearchPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def search(self, term):
        """list all photo sets, videos, models and sites that match search term"""
        order = self.get_order("search")
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


class HtmlPhotoSetPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def do_gallery(self, idx, col, val, table, links):
        """single photo set page"""
        #picwidth = {'thumb':9, 'small':24, 'medium':48, 'large':98}
        #columns = {'thumb':11, 'small':4, 'medium':2, 'large':1}
        mids = []
        psets = self.db.photos_table().select_where('id', idx)

        try:
            mids = [{'name': self.db.models_table().select_where('id', x[1])[0][1],'href':f"/{self.dbname}/model/{x[1]}"} for x in psets]
        except IndexError:
            mids = [{'name': '','href':""} for x in psets]

        idx, model_id, site_id, name, location, thumb, count, pdate = psets[0]

        sitename = self.db.sites_table().select_where('id', site_id)[0][1]
        try:
            modelname = self.db.models_table().select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''


        if count < 25:
            gallery = self.create_gallery(location, idx, count, False)
        else:
            gallery = self.create_gallery(location, idx, count, True)

        nphoto, pphoto, nname, pname = self.db.photos_table().get_next_prev(idx, col, val)

        titledict = {'site': {'href':f"/{self.dbname}/site/{site_id}",
                              'name':sitename},
                     'models': mids,
                     'folder': name}
        prefix = ''
        if table is not None:
            prefix += table+'/'
        if val is not None:
            prefix += val+'/'


        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(titledict, False, 'gallery', links)
        page_dict['prefix'] = prefix
        page_dict['nid'] = nphoto
        page_dict['pid'] = pphoto
        page_dict['next'] = nname
        page_dict['prev'] = pname
        page_dict['count'] = len(gallery)
        if count < 25:
            page_dict['columns'] = 2
        else:
            page_dict['columns'] = 12

        return render_template("photo_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               gallpage=gallery
                               )


    #def old_create_gallery(self, fld, _idx, count):
    #    """relies on knowing the format of the image file name"""
    #    gall = []
    #    for i in range(count):
    #        n = i+1
    #        pic = os.path.basename(fld)
    #        image = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{pic}_{n}.jpg"
    #        gall.append({'href':image,
    #                     'src':image}
    #                     )
    #    return gall


    def create_gallery(self, fld, _idx, _count, use_thms=False):
        """relies on being able to downloading the list of images from the gallery server"""
        # eg. self.config['webroot']/zdata/stuff.backup/sdc1/www.hegre-art.com/members//LubaAfterAShowerGen/

        gall = []
        url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/".replace(' ','%20').replace('[',r'\[').replace(']',r'\]')
        #print(f"{url}")
        st, out = unix(f"curl -s \"{url}\"")
        if st != 0:
            print(f"{url} - {st} {out}")
        #print(f"{out}")
        for line in out.split('\n'):
            if line.find("[IMG]") > -1:
                img = line[line.find("href="):line.find("</a>")].split('"')[1]
                imgurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{img}"
                picurl = imgurl
                if use_thms:
                    picurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/.pics/{img.replace('jpg','png')}"
                gall.append({'href': imgurl,
                             'src': picurl,
                             'pic': img}
                             )
        if len(gall) == 0:
            print(f"{url} - {st} {out}")
        return gall


class PageInfo:
    def __init__(self, tagdicts, name, filtid=''):
        self.name = name
        self.tagdicts = tagdicts
        self.filtcol = '' if filtid=='' else name
        self.filtid = filtid


class HtmlModelPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self.modelid = None

    def do_page(self, modelid):
        """list all photo sets and videos of a model"""
        self.modelid = modelid
        #modelpage = ModelPage([self.galdict, self.viddict], modelid, self.db)
        info = PageInfo([self.galdict, self.viddict], 'model', filtid=modelid)
        pagebuilder = PageBuilder(info, self)
        page_dict, gvdicts = pagebuilder.build()

        # next/prev needs to follow sort order of models page above
        nmodel, pmodel, nname, pname = self.db.models_table().get_next_prev(modelid)

        page_dict['nid'] = nmodel
        page_dict['pid'] = pmodel
        page_dict['next'] = nname
        page_dict['prev'] = pname

        modelname = self.db.models_table().select_where('id', modelid)[0][1]
        page_dict['title'] = modelname

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=gvdicts[0],
                               viddicts=gvdicts[1])

    def getitems(self, order):
        order_by = {
            'alpha': 'asc',  'ralpha': 'desc',
            'id':    'asc',  'rid':    'desc',
            'date':  'asc',  'rdate':  'desc'
            }
        unsorted_photos = self.db.photos_table().select_where_group_by('model_id',self.modelid,'id')
        #    id, model_id, site_id, name, location, thumb, count, pdate = gallery
        unsorted_videos = self.db.videos_table().select_where_group_by('model_id',self.modelid,'id')

        # lambda is setting the database column to sort on - date is different between photos and videos
        if order in ('alpha', 'ralpha'):
            photos = sorted(unsorted_photos, key = lambda x: x[3]) #name
            videos = sorted(unsorted_videos, key = lambda x: x[3])
        elif order in ('id', 'rid'):
            photos = sorted(unsorted_photos, key = lambda x: x[0]) # id
            videos = sorted(unsorted_videos, key = lambda x: x[0])
        elif order in ('date', 'rdate'):
            photos = sorted(unsorted_photos, key = lambda x: x[7])  #pdate
            videos = sorted(unsorted_videos, key = lambda x: x[10]) #vdate

        if order_by[order] == 'desc':
            photos.reverse()
            videos.reverse()
        return (photos, videos)



class HtmlSitePage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self.siteid = None

    def do_page(self, siteid):
        """list all photo sets amd videos of a site"""
        self.siteid = siteid
        #sitepage = SitePage([self.galdict, self.viddict], siteid, self.db)
        info = PageInfo([self.galdict, self.viddict], 'site', filtid=siteid)
        pagebuilder = PageBuilder(info, self)
        page_dict, gvdicts = pagebuilder.build()

        # next/prev needs to follow sort order of sites page above
        nsite, psite, nname, pname = self.db.sites_table().get_next_prev(siteid)

        page_dict['nid'] = nsite
        page_dict['pid'] = psite
        page_dict['next'] = nname
        page_dict['prev'] = pname

        sitename = self.db.sites_table().select_where('id', self.siteid)[0][1]
        page_dict['title'] = sitename

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=gvdicts[0],
                               viddicts=gvdicts[1])

    def getitems(self, order):
        photos = self.db.photos_table().select_where_order_by('site_id', self.siteid, sorting[order][0], sorting[order][2])
        videos = self.db.videos_table().select_where_order_by('site_id', self.siteid, vsorting[order][0], vsorting[order][2])
        return (photos, videos)


class HtmlVideoPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def do_page(self, vid, page=None, pageid=None): #sid=None, mid=None):
        """single video page"""
        video = self.db.videos_table().select_where('id', vid)[0]
        idx, model_id, site_id, name, filename, thumb, poster, width, height, length, vdate = video
        if poster is None or poster == "":
            poster = thumb
        sitename = self.db.sites_table().select_where('id', site_id)[0][1]
        try:
            modelname = self.db.models_table().select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''
        if self.dbname == "hegre":
            filename = filename.replace('.avi', '.mp4')

        thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
        video_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['videos']}/{filename}"
        if int(width) > 1280 or int(height) > 720:
            width=1280
            height=720
        if int(width) == 0:
            width=1280
            height=720

        viddict = {'height':height, 'width':width, 'thumb_url':thumb_url, 'video_url':video_url}

        if page is None: #mid is None and sid is None:
            nvideo, pvideo, nname, pname = self.db.videos_table().get_next_prev(vid)
        else:
            nvideo, pvideo, nname, pname = self.db.videos_table().get_next_prev(vid, f'{page}_id', pageid)

        sys.stderr.write(f"nv {nvideo}, pv{pvideo}, nn {nname}, pn {pname}\n")

        links = self.heading('videos')
        prefix = f"{page}/{pageid}/" if page is not None else ""

        titledict = {
            'site': {'href':f"/{self.dbname}/site/{site_id}",
                     'name':sitename},
            'models':[{'href':f"/{self.dbname}/model/{model_id}",
                       'name':modelname}],
            'folder': name
        }

        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(titledict, False, 'video', links)
        page_dict['nid'] = nvideo
        page_dict['pid'] = pvideo
        page_dict['next'] = nname
        page_dict['prev'] = pname
        page_dict['prefix'] = prefix

        sys.stderr.write(f"page_dict = {page_dict}\n")

        return render_template("video_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddict=viddict)


class HtmlPhotosPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all photo sets"""
        #photospage = PhotosPage([self.galdict,], self.db.photos_table())
        info = PageInfo([self.galdict,], 'photos')
        pagebuilder = PageBuilder(info, self)
        page_dict, galldicts = pagebuilder.build()
        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts[0])

    def getitems(self, order):
        items = self.db.photos_table().select_order_by(sorting[order][1], sorting[order][2])
        if len(items) == 0:
            items = self.db.photos_table().select_group_by_order_by('id', 'id', 'desc')
        return (items,)


class HtmlVideosPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all videos"""
        #videospage = VideosPage([self.viddict,], self.db.videos_table())
        info = PageInfo([self.viddict,], 'videos')
        pagebuilder = PageBuilder(info, self)
        page_dict, viddicts = pagebuilder.build()
        return render_template("videos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddicts=viddicts[0])

    def getitems(self, order):
        items = self.db.videos_table().select_order_by(vsorting[order][1], vsorting[order][2])
        if len(items) == 0:
            items = self.db.videos_table().select_group_by_order_by('id', 'id', 'desc')
        return (items,)



class HtmlSitesPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all sites"""
        #sitespage = SitesPage([self.sitdict,], self.db.sites_table())
        info = PageInfo([self.sitdict,], 'sites')
        pagebuilder = PageBuilder(info, self)
        page_dict, galldicts = pagebuilder.build()
        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts[0])

    def getitems(self, order):
        order_by = {'most': 'desc', 'least': 'asc'}

        if order in ['most', 'least']:
            sites = self.db.sites_table().select_sites_by_count(order_by[order])
        else:
            sites = self.db.sites_table().select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
        return (sites,)


class HtmlModelsPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all models"""
        #modelspage = ModelsPage([self.moddict,], self.db.models_table())
        info = PageInfo([self.moddict,], 'models')
        pagebuilder = PageBuilder(info, self)
        page_dict, galldicts = pagebuilder.build()
        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts[0])

    def getitems(self, order):
        order_by = {
            'alpha':   'asc',   'ralpha':   'desc',
            'vlatest': 'desc',  'rvlatest': 'asc',
            'platest': 'desc',  'rplatest': 'asc',
            'most':    'desc',  'least':    'asc',
            'id':      'asc',   'rid':      'desc'
        }
        if order in ['alpha', 'ralpha']:
            models = self.db.models_table().select_group_by_order_by('name', 'name', order_by[order])

        elif order in ['vlatest', 'rvlatest']:
            models = self.db.models_table().select_by_most_recent_videos('model_id', order_by[order])

        elif order in ['platest', 'rplatest']:
            models = self.db.models_table().select_by_most_recent_photos('model_id', order_by[order])

        elif order in ['most', 'least']:
            models = self.db.models_table().select_models_by_count(order_by[order])

        elif order in ['id', 'rid']:
            models = self.db.models_table().select_order_by('id', order_by[order])

        if len(models) == 0:
            models = self.db.models_table().select_order_by('id', 'desc')

        return (models,)


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
                error_occured = True
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
            'title': f"Random Selection From All",
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
                error_occured = True
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

        links = self.htmlpage.heading(self.info.name)
        page_dict = self.htmlpage.init_page_dict('', True, self.info.name, links)
        page_dict['search'] = True
        return page_dict, tagdicts


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
