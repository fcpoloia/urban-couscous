#!/usr/bin/env python3

# Mark II verion of the website using a different database schema

from flask import Flask, request, render_template, session
import glob, os
from subprocess import getstatusoutput as unix

from .db2 import ConfigTable, ModelsTable, SitesTable, PhotosTable, VideosTable, DatabaseMissingError
from sqlite3 import OperationalError

DATABASE = "flaskr/new_kindgirls.db"


def getDBpath(dbname):
    """"""
    return f"flaskr/new_{dbname}.db"


def databaseButtons():
    """"""
    sql = "SELECT title FROM config;"
    buttons = []
    names = []
    dblist = {}
    for database in glob.glob("flaskr/new_*.db"):
        dbname = database.replace("flaskr/new_",'').replace('.db','')
        name = ConfigTable(database).get_single_result(sql,1)[0]
        dblist[dbname] = name
        names.append(dbname)
    names.sort()
    for dbname in names:
        buttons.append({'href':'/'+dbname, 'name':dblist[dbname]})

    page_dict = {
        'title':'',
        'heading':'Stuff',
        'plaintitle':True,
        'button_class':'fivebuttons'
    }
    return buttons, page_dict


def random_selection(datalist, count):
    """"""
    if len(datalist) <= 1:
        return datalist

    import random
    selection = []
    nums = []

    while len(selection) < count:
        num = random.randrange(len(datalist))
        if num not in nums:
            nums.append(num)
            selection.append(datalist[num])
    return selection


def siteRoot():
    """"""
    buttons, page_dict = databaseButtons()
    return render_template("intro.html",
                           webroot="http://"+request.host.replace(':5000',''),
                           page=page_dict,
                           buttons=buttons)


def get_order(order):
    """"""
    if 'order' in session:
        order = session['order']
    return order


def get_page_num(page):
    """"""
    if 'page' in session:
        page = session['page']
    return page


def get_config(dbname):
    """"""
    global DATABASE
    DATABASE = f"flaskr/new_{dbname}.db"
    #print(DATABASE)
    try:
        vals = ConfigTable(DATABASE).select_all()[0]
        cols = ConfigTable(DATABASE).column_list()
        config = {}
        if len(vals) == len(cols):
            for i in range(len(cols)):
                config[cols[i]] = vals[i]
        #print(config)
    except DatabaseMissingError:
        raise
    # fix the webroot so that it copes with both name or ip provided in url
    config['webroot'] = "http://"+request.host.replace(':5000','')
    return config


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


class HtmlSite:

    def __init__(self, dbname):
        """"""
        self.errorOccured = False
        self.dbname = dbname
        self.pg = {'next':-1, 'prev':-1}
        try:
            self.config = get_config(dbname)
        except DatabaseMissingError:
            self.errorOccured = True
        self.default_thumbsize = 240
        self.thumb_h = 240
        self.pgcount = 500


    def setThumbSize(self):
        """"""
        if 'thumbsize' in session:
            if 'thumb_h' not in session:
                session['thumb_h'] = self.default_thumbsize
            if session['thumbsize'] == "large":
                self.thumb_h = self.default_thumbsize
            elif session['thumbsize'] == "small":
                self.thumb_h = self.default_thumbsize / 1.5


    def do(self, method, *args):
        """"""
        try:
            func = getattr(self, method)
        except AttributeError:
            print(f"AttributeError: {method} ( )")
            print(*args)
            return
        return func(*args)


    def heading(self, page=None):
        """"""
        links = {
            "photos": {"href": f"/{self.dbname}/photos", "title": "Photos", 'class':'', 'rows': PhotosTable(DATABASE).row_count() },
            "models": {"href": f"/{self.dbname}/models", "title": "Girls",  'class':'', 'rows': ModelsTable(DATABASE).row_count() },
            "sites":  {"href": f"/{self.dbname}/sites",  "title": "Sites",  'class':'', 'rows': SitesTable(DATABASE).row_count()-1 },
            "videos": {"href": f"/{self.dbname}/videos", "title": "Videos", 'class':'', 'rows': VideosTable(DATABASE).row_count() }
            }

        if page is not None:
            links[page]['class'] = " page"

        return links


    def getConfig(self):
        """"""
        return self.config


    def page_range(self, num, total):
        """"""
        self.pg = {'next': num+1 if (num) * self.pgcount < total else 0,
                   'prev': num-1 if (num-1) > 0 else 0}
        return (num-1)*self.pgcount, (num*self.pgcount)-1


    def moddict(self, models, pgnum=1):
        """"""
        cmodels = ModelsTable(DATABASE).get_model_set_count()
        mdicts = []
        sidx, eidx = self.page_range(pgnum, len(models))
        for id,name,thumb in models[sidx:eidx]:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href': f"/{self.dbname}/model/{id}",
                           'src': thumburl,
                           'name': name,
                           'height': self.thumb_h,
                           'count': cmodels[id]}
                           )
        return (len(models) > 0), mdicts


    def galdict(self, photos, filter='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filter != '':
            filterurl = f"/{filter}/{filtid}"
        gdict = []
        sidx, eidx = self.page_range(pgnum, len(photos))
        for gallery in photos[sidx:eidx]:
            id, model_id, site_id, name, location, thumb, count, pdate = gallery
            thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thumb}"
            #name = name.replace('_', ' ')[:50]
            gdict.append({'href': f"/{self.dbname}/gallery{filterurl}/{id}",
                          'src': thumb,
                          'name': name.replace('_', ' ')[:50],
                          'height': self.thumb_h,
                          'count': count}
                          )
        return (len(photos) > 0), gdict


    def viddict(self, videos, filter='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filter != '':
            filterurl=f"/{filter}/{filtid}"
        vdicts = []
        sidx, eidx = self.page_range(pgnum, len(videos))
        for vid in videos[sidx:eidx]:
            id, model_id, site_id, name, filename, thumb, poster, width, height, length, vdate = vid
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            vdicts.append({'href':f"/{self.dbname}/video{filterurl}/{id}",
                           'src':thumb_url,
                           'name':name,
                           'theight':self.thumb_h,
                           'w': width,
                           'h': height,
                           'mlen':human_time(length)}
                           )
        return (len(videos) > 0),vdicts


    def sitdict(self, sites):
        """"""
        sites_count = {}
        csites = SitesTable(DATABASE).get_sites_set_count()
        ordered_sites = {}
        sdict = []
        for id,name,location in sites:
            try:
                pid,_,_,_,_,thm = PhotosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][:6]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
                sdict.append({'href':f"/{self.dbname}/site/{id}",
                              'src':thumb,
                              'name':name,
                              'height':self.thumb_h,
                              'count': csites[id]}
                              )
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
                sdict.append({'href':f"/{self.dbname}/site/{id}",
                              'src':thumb,
                              'name':name,
                              'height':self.thumb_h,
                              'count': csites[id]}
                              )
        return (len(sites) > 0), sdict


    def init_page_dict(self, title, plaintitle, ptype, links):
        """"""
        return {
            'title':title, 'db':self.dbname, 'heading':self.config['title'],
            'plaintitle':plaintitle, 'navigation':links, 'type':ptype, 'pg':self.pg,
            'url': request.base_url
        }


    def models(self):
        """"""
        models = []
        pgnum = get_page_num(1)
        order = get_order("most")
        if self.dbname == 'inthecrack': order = get_order("vlatest")

        order_by = {
            'alpha': 'asc',    'ralpha': 'desc',
            'vlatest': 'desc', 'rvlatest': 'asc',
            'platest': 'desc', 'rplatest': 'asc',
            'most': 'desc',    'least': 'asc',
            'id': 'asc',       'rid': 'desc'
        }
        if order in ['alpha', 'ralpha']:
            models = ModelsTable(DATABASE).select_group_by_order_by('name', 'name', order_by[order])

        elif order in ['vlatest', 'rvlatest']:
            models = ModelsTable(DATABASE).select_by_most_recent_videos('model_id', order_by[order])

        elif order in ['platest', 'rplatest']:
            models = ModelsTable(DATABASE).select_by_most_recent_photos('model_id', order_by[order])

        elif order in ['most', 'least']:
            models = ModelsTable(DATABASE).select_models_by_count(order_by[order])

        elif order in ['id', 'rid']:
            models = ModelsTable(DATABASE).select_order_by('id', order_by[order])

        if len(models) == 0:
            models = ModelsTable(DATABASE).select_order_by('id', 'desc')

        _hasmodels, galldicts = self.moddict(models, pgnum=pgnum)

        links = self.heading('models')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('',True,'models',links)
        page_dict['search'] = True

        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def model(self, modelid):
        """"""
        order = get_order('alpha')

        order_by = {
            'alpha': 'asc', 'ralpha': 'desc',
            'id': 'asc',    'rid': 'desc',
            'date': 'asc',  'rdate': 'desc'
            }
        unsorted_photos = PhotosTable(DATABASE).select_where_group_by('model_id',modelid,'id')
        #    id, model_id, site_id, name, location, thumb, count, pdate = gallery
        if order == 'alpha' or order == 'ralpha':
            photos = sorted(unsorted_photos, key = lambda x: x[3])
        elif order == 'id' or order == 'rid':
            photos = sorted(unsorted_photos, key = lambda x: x[0])
        elif order == 'date' or order == 'rdate':
            photos = sorted(unsorted_photos, key = lambda x: x[7])

        if order_by[order] == 'desc':
            photos.reverse()

        videos = VideosTable(DATABASE).select_where_group_by('model_id',modelid,'id')
        modelname = ModelsTable(DATABASE).select_where('id',modelid)[0][1]

        _hasphotos, galldicts = self.galdict(photos, 'model', modelid)

        _hasvideos, viddicts = self.viddict(videos, 'model', modelid)

        # next/prev needs to follow sort order of models page above
        #print(f"(model) get_next_prev modelid={modelid}")
        nmodel, pmodel, nname, pname = ModelsTable(DATABASE).get_next_prev(modelid)

        links = self.heading('models')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(modelname,True,'model',links)
        page_dict['nid'] = nmodel
        page_dict['pid'] = pmodel
        page_dict['next'] = nname
        page_dict['prev'] = pname

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts,
                               viddicts=viddicts)


    def sites(self):
        """"""
        sites = []
        order = get_order("most")

        sorting = {
            'alpha':  ('name','name','asc'),
            'ralpha': ('name','name','desc'),
            'id':     ('id','id','asc'),
            'rid':    ('id','id','desc')
        }
        order_by = {'most': 'desc', 'least': 'asc'}

        if order in ['most', 'least']:
            sites = SitesTable(DATABASE).select_sites_by_count(order_by[order])
        else:
            sites = SitesTable(DATABASE).select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])

        _hassites, galldicts = self.sitdict(sites)

        links = self.heading('sites')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('',True,'sites',links)
        page_dict['search'] = True

        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def site(self, siteid):
        """"""
        order = get_order("alpha")
        sorting = {'alpha': ['name','name','asc'],
                   'ralpha':['name','name','desc'],
                   'id':    ['id','id','asc'],
                   'rid':   ['id','id','desc'],
                   'date':   ['pdate','pdate','asc'],
                   'rdate':  ['pdate','pdate','desc']
                   }
        sitename = SitesTable(DATABASE).select_where('id', siteid)[0][1]
        photos = PhotosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, sorting[order][0], sorting[order][1], sorting[order][2])
        if order in ['date', 'rdate']:
            sorting[order][0] = "vdate"
            sorting[order][1] = "vdate"
        videos = VideosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, sorting[order][0], sorting[order][1], sorting[order][2])

        _hasphotos, galldicts = self.galdict(photos, 'site', siteid)

        _hasvideos, viddicts = self.viddict(videos, 'site', siteid)

        #print(f"(site) get_next_prev siteid={siteid}")
        nsite, psite, nname, pname = SitesTable(DATABASE).get_next_prev(siteid)

        links = self.heading('sites')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(sitename,True,'site',links)
        page_dict['nid'] = nsite
        page_dict['pid'] = psite
        page_dict['next'] = nname
        page_dict['prev'] = pname

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts,
                               viddicts=viddicts)


    def photos(self):
        """"""
        photos = []
        pgnum = get_page_num(1)
        order = get_order("rid")

        sorting = {
            'alpha':  ('name','name','asc'),
            'ralpha': ('name','name','desc'),
            'pics':   ('id','count','desc'),
            'rpics':  ('id','count','asc'),
            'id':     ('id','id','asc'),
            'rid':    ('id','id','desc'),
            'date':   ('pdate','pdate','asc'),
            'rdate':  ('pdate','pdate','desc')
        }
        #photos = PhotosTable(DATABASE).select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
        #photos = PhotosTable(DATABASE).select_group_by_order_by('site_id', sorting[order][1], sorting[order][2])
        photos = PhotosTable(DATABASE).select_order_by(sorting[order][1], sorting[order][2])

        if len(photos) == 0:
            photos = PhotosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')

        _hasphotos, galldicts = self.galdict(photos, pgnum=pgnum)

        links = self.heading('photos')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('',True,'photos',links)
        page_dict['search'] = True

        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def videos(self):
        """"""
        pgnum = get_page_num(1)
        order = get_order("rid")
        #print(f"videos order {order}")

        sorting = {
            'alpha':   ('name','name','asc'),
            'ralpha':  ('name','name','desc'),
            #'rlatest': ('id','id','desc'),
            #'latest':  ('id','id','asc'),
            'id':      ('id','id','asc'),
            'rid':     ('id','id','desc'),
            'date':    ('vdate','vdate','asc'),
            'rdate':   ('vdate','vdate','desc'),
        }
        #videos = VideosTable(DATABASE).select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
        #videos = VideosTable(DATABASE).select_group_by_order_by('name', sorting[order][1], sorting[order][2])
        videos = VideosTable(DATABASE).select_order_by(sorting[order][1], sorting[order][2])
        print(f"len(videos) = {len(videos)}")

        _hasvideos, viddicts = self.viddict(videos, pgnum=pgnum)

        links = self.heading('videos')
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('',True,'videos',links)
        page_dict['search'] = True
        print(page_dict)

        return render_template("videos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddicts=viddicts)


    def video(self, vid, sid=None, mid=None):
        """"""
        video = VideosTable(DATABASE).select_where('id', vid)[0]
        id, model_id, site_id, name, filename, thumb, poster, width, height, length, vdate = video
        if poster is None or poster == "":
            poster = thumb
        sitename = SitesTable(DATABASE).select_where('id', site_id)[0][1]
        try:
            modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
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

        nvideo = pvideo = nname = pname = None
        #print(f"(video) get_next_prev vid={vid} site_id={sid}")
        if sid is not None:
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'site_id', sid)
        #print(f"(video) get_next_prev vid={vid} model_id {mid}")
        if mid is not None:
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'model_id', mid)
        if mid is None and sid is None:
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid)


        links = self.heading('videos')
        prefix = ''
        if sid is not None: prefix+=f"site/{sid}/"
        if mid is not None: prefix+=f"model/{mid}/"

        titledict = {
            'site': {'href':f"/{self.dbname}/site/{site_id}",
                     'name':sitename},
            'models':[{'href':f"/{self.dbname}/model/{model_id}",
                       'name':modelname}],
            'folder': name
        }
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(titledict,False,'video',links)
        page_dict['nid'] = nvideo
        page_dict['pid'] = pvideo
        page_dict['next'] = nname
        page_dict['prev'] = pname
        page_dict['prefix'] = prefix

        return render_template("video_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddict=viddict)


    def do_gallery(self, id, col, val, table, links):
        """"""
        picwidth = {'thumb':9, 'small':24, 'medium':48, 'large':98}
        columns = {'thumb':11, 'small':4, 'medium':2, 'large':1}
        mids = []
        psets = PhotosTable(DATABASE).select_where('id', id)

        try:
            mids = [{'name': ModelsTable(DATABASE).select_where('id', x[1])[0][1],'href':f"/{self.dbname}/model/{x[1]}"} for x in psets]
        except IndexError:
            mids = [{'name': '','href':f""} for x in psets]

        id, model_id, site_id, name, location, thumb, count, pdate = psets[0]

        sitename = SitesTable(DATABASE).select_where('id', site_id)[0][1]
        try:
            modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''


        def getpicwidth():
            if 'imagesize' in session:
                return picwidth[session['imagesize']]
            return picwidth['large']

        def getcolumns():
            if 'imagesize' in session:
                return columns[session['imagesize']]
            return columns['large']


        gallery = self.create_gallery(location, id, count, getpicwidth())

        #print(f"(do_gallery) get_next_prev pid={id} {col}={val}")
        next, prev, nname, pname = PhotosTable(DATABASE).get_next_prev(id, col, val)

        titledict = {'site': {'href':f"/{self.dbname}/site/{site_id}",
                              'name':sitename},
                     'models': mids, #{'href':f"/{self.dbname}/model/{model_id}", 'name':modelname},
                     'folder': name}
        prefix = ''
        if table is not None: prefix += table+'/'
        if val is not None: prefix += val+'/'


        #print(f"{session}")
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(titledict,False,'gallery',links)
        page_dict['prefix'] = prefix
        page_dict['nid'] = next
        page_dict['pid'] = prev
        page_dict['next'] = nname
        page_dict['prev'] = pname
        page_dict['count'] = len(gallery)
        page_dict['columns'] = getcolumns()
        page_dict['picwidth'] = getpicwidth()

        return render_template("photo_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               gallpage=gallery
                               )


    def old_create_gallery(self, fld, id, count):
        """relies on knowing the format of the image file name"""
        gall = []
        for i in range(count):
            n = i+1
            pic = os.path.basename(fld)
            image = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{pic}_{n}.jpg"
            gall.append({'href':image,
                         'src':image}
                         )
        return gall


    def create_gallery(self, fld, id, count, picsize):
        """relies on being able to downloading the list of images from the gallery server"""
        # eg. self.config['webroot']/zdata/stuff.backup/sdc1/www.hegre-art.com/members//LubaAfterAShowerGen/

        gall = []
        url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/".replace(' ','%20').replace('[','\[').replace(']','\]')
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
                if picsize == 9:
                    picurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/.pics/{img.replace('jpg','png')}"
                gall.append({'href': imgurl,
                             'src': picurl,
                             'pic': img}
                             )
        if len(gall) == 0:
            print(f"{url} - {st} {out}")
        return gall


    def search(self, term):
        """"""
        order = get_order("alpha")
        #term = get_search()

        sites = SitesTable(DATABASE).select_where_like('name', term)
        models = ModelsTable(DATABASE).select_where_like('name', term)
        photos = PhotosTable(DATABASE).select_where_like_group_order('name', term, 'id', 'id', 'desc')
        videos = VideosTable(DATABASE).select_where_like_group_order('name', term, 'id', 'id', 'desc')

        _hasmodels, modeldicts = self.moddict(models)
        _hasphotos, galldicts = self.galdict(photos)
        _hasvideos, viddicts = self.viddict(videos)
        _hassites, sitedicts = self.sitdict(sites)

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


    def random(self):
        """"""
        sites = SitesTable(DATABASE).select_all()
        models = ModelsTable(DATABASE).select_all()
        photos = PhotosTable(DATABASE).select_all()
        videos = VideosTable(DATABASE).select_all()

        models = random_selection(models, 8)
        photos = random_selection(photos, 8)
        videos = random_selection(videos, 4)

        _hasmodels, modeldicts = self.moddict(models)
        _hasphotos, galldicts = self.galdict(photos)
        _hasvideos, viddicts = self.viddict(videos)

        links = self.heading()
        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict('Random Selection',True,'random',links)
        page_dict['search'] = True

        return render_template("search_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict, #search_term=s,
                               galldicts=galldicts,
                               modeldicts=modeldicts,
                               viddicts=viddicts,
                               pagetype='random')


    def rootpage(self):
        """"""
        buttons = [
            {'href':f"/{self.dbname}/photos", 'name':'Photos'},
            {'href':f"/{self.dbname}/models", 'name':'Models'},
            {'href':f"/{self.dbname}/sites",  'name':'Sites'},
            {'href':f"/{self.dbname}/videos", 'name':'Videos'},
        ]

        links = self.heading()
        # title plaintitle heading type
        page_dict = self.init_page_dict('',True,'',links)
        page_dict['button_class'] = 'fourbuttons'

        return render_template("intro.html",
                               webroot=self.getConfig()['webroot'],
                               page=page_dict,
                               buttons=buttons)


class Page:
    def __init__(self):
        pass

    def render(self):
        return render_template(self.pagehtml)

class IntroPage:
    def __init__(self):
        super().__init__(dbname, 'models')


#    def edit(self, table, id):
#        """"""
#        photo = PhotosTable(DATABASE).select_where('id', id)
#        models = ModelsTable(DATABASE).select_order_by('name', 'asc')
#        mopts = {}
#        for model in models:
#            mopts[model[0]] = model[1]
#        links = self.heading()
#        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'button_class':'fourbuttons'}
#        return render_template("edit_page.html",
#                               webroot=self.getConfig()['webroot'],
#                               page=page_dict,
#                               editphoto=photo,
#                               modelist=mopts
#                             )
