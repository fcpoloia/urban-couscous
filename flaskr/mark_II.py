#!/usr/bin/env python3

# Mark II verion of the website using a different database schema

from flask import Flask, render_template, session
import glob, os
from subprocess import getstatusoutput as unix

from .db2 import ConfigTable, ModelsTable, SitesTable, PhotosTable, VideosTable, DatabaseMissingError
from sqlite3 import OperationalError

DATABASE = "flaskr/new_kindgirls.db"

class SiteDB:
    def __init__(self, dbname):
        self.dbname = dbname

def getDBpath(dbname):
    return f"flaskr/new_{dbname}.db"

def databaseButtons():
    """"""
    buttons = [{'href':'/kindgirls',  'name':'KindGirls'},
               {'href':'/inthecrack', 'name':'InTheCrack'},
               {'href':'/hegre',      'name':'Hegre-Art'},
               {'href':'/alsangels',  'name':'AlsAngels'},
               {'href':'/alsscans',   'name':'ALSScans'},
               {'href':'/femjoy',     'name':'FemJoy'}
           ]
    page_dict = {'title':'', 'heading':'Stuff', 'plaintitle':True, 'button_class':'fivebuttons'}
    return buttons, page_dict

def random_selection(datalist, count):
    """"""
    import random
    selection = []
    nums = []
    if len(datalist) > 1:
        while len(selection) < count:
            num = random.randrange(len(datalist))
            if num not in nums:
                nums.append(num)
                selection.append(datalist[num])
        return selection
    else:
        return datalist

def siteRoot():
    """"""
    buttons, page_dict = databaseButtons()
    return render_template("intro.html", 
                           webroot="http://gallery", #mysite.getConfig()['webroot'],
                           page=page_dict, 
                           buttons=buttons)

def get_order(default):
    order = default
    if 'order' in session:
        order = session['order']
    print(f"photos order {order}")
    return order

def get_config(dbname):
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
        try:
            self.config = get_config(dbname)
        except DatabaseMissingError:
            self.errorOccured = True
        self.default_thumbsize = 120
        self.thumb_h = 120

    def setThumbSize(self):
        if 'thumbsize' in session:
            if 'thumb_h' not in session:
                session['thumb_h'] = self.default_thumbsize
            if session['thumbsize'] == "large":
                self.thumb_h = 1.5 * self.default_thumbsize
                print(f"thumb_h = {self.thumb_h}")
            elif session['thumbsize'] == "small":
                self.thumb_h = self.default_thumbsize
                print(f"thumb_h = {self.thumb_h}")
                
            elif session['thumbsize'] == "inc":
                session['thumb_h'] = session['thumb_h']+10
                self.thumb_h = session['thumb_h']
                print(f"thumb_h = {self.thumb_h}")
            elif session['thumbsize'] == "dec":
                session['thumb_h'] = session['thumb_h']-10
                self.thumb_h = session['thumb_h']
                print(f"thumb_h = {self.thumb_h}")
            

    def do(self, method, *args):
        try:
            func = getattr(self, method) #(*args)
        except AttributeError:
            print(f"AttributeError: {method} ( )")
            print(*args)
            return
        return func(*args)

    def heading(self, page=None):
        """"""
        links = {
            "photos": {"href": f"/{self.dbname}/photos", "title": "Photos", 'class':''},
            "models": {"href": f"/{self.dbname}/models", "title": "Girls",  'class':''},
            "sites":  {"href": f"/{self.dbname}/sites",  "title": "Sites",  'class':''},
            "videos": {"href": f"/{self.dbname}/videos", "title": "Videos", 'class':''}}
            
        if page is not None:
            links[page]['class'] = " page"
            
        return links

    def getConfig(self):
        """"""
        return self.config

    def moddict(self, models):
        """"""
        mdicts = []
        for id,name,thumb in models:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href':f"/{self.dbname}/model/{id}", 'src':thumburl, 'name':name, 'height':self.thumb_h})
        return (len(models) > 0), mdicts


    def galdict(self, photos, filter='', filtid=''):
        """"""
        filterurl=""
        if filter != '':
            filterurl = f"/{filter}/{filtid}"
        gdict = []
        for gallery in photos[:1000]:
            id, model_id, site_id, name, location, thumb, count = gallery
            thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thumb}" #.replace(' ','%20')
            name = name.replace('_', ' ')[:50]
            gdict.append({'href':f"/{self.dbname}/gallery{filterurl}/{id}", 'src':thumb, 'height':self.thumb_h, 'name': name, 'count': count})
        return (len(photos) > 0), gdict


    def viddict(self, videos, filter='', filtid=''):
        """"""
        filterurl=""
        if filter != '':
            filterurl=f"/{filter}/{filtid}"
        vdicts = []
        for vid in videos:
            id, model_id, site_id, name, filename, thumb, width, height, length = vid
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            vdicts.append({'href':f"/{self.dbname}/video{filterurl}/{id}", 'src':thumb_url, 'name':name, 'theight':self.thumb_h, 
                             'w': width, 'h': height, 'mlen':human_time(length)})
            #print(self.thumb_h)
        return (len(videos) > 0),vdicts

    def sitdict(self, sites):
        """"""
        ordered_sites = {}
        sdict = []
        for id,name,location in sites:
            try:
                pid,_,_,_,_,thm = PhotosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][:6]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
        photo_ids = [k for k in ordered_sites]
        photo_ids.sort()
        photo_ids.reverse()
        for pid in photo_ids:
            sdict.append(ordered_sites[pid])
        return (len(sites) > 0), sdict


    def models(self):
        """"""
        order = get_order("platest")
        
        if order == "alpha":
            models = ModelsTable(DATABASE).select_group_by_order_by('name', 'name', 'asc')
            print(f"alpha {len(models)}")
        elif order == "ralpha":
            models = ModelsTable(DATABASE).select_group_by_order_by('name', 'name', 'desc')
            print(f"ralpha {len(models)}")
        elif order == "latest": # or order == None: # latest video
            models = ModelsTable(DATABASE).select_by_most_recent_videos('model_id', 'desc')
            print(f"latest {len(models)}")
        elif order == "rlatest": # latest video
            models = ModelsTable(DATABASE).select_by_most_recent_videos('model_id', 'asc')
            print(f"rlatest {len(models)}")
        elif order == "platest": # or order == None or order in ("small", "large"): # latest video
            models = ModelsTable(DATABASE).select_by_most_recent_photos('model_id', 'desc')
            print(f"platest {len(models)}")
        elif order == "most":
            models = ModelsTable(DATABASE).select_models_by_count('desc')
            print(f"most {len(models)}")
        elif order == "least":
            models = ModelsTable(DATABASE).select_models_by_count('asc')
            print(f"least {len(models)}")

        #if order == "2x":
        #    self.thumb_h = self.thumb_h * 1.6

        if len(models) == 0:
            models = ModelsTable(DATABASE).select_order_by('id', 'desc')
        
        hasmodels, galldicts = self.moddict(models)
        
        links = self.heading('models')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 
                     'db':self.dbname, 'search': True, 'type':'models'}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)

    def model(self, modelid):
        """"""
        photos = PhotosTable(DATABASE).select_where('model_id',modelid)
        videos = VideosTable(DATABASE).select_where('model_id',modelid)
        modelname = ModelsTable(DATABASE).select_where('id',modelid)[0][1]
    
        hasphotos, galldicts = self.galdict(photos, 'model', modelid)

        hasvideos, viddicts = self.viddict(videos, 'model', modelid)
    
        # next/prev needs to follow sort order of models page above
        print(f"(model) get_next_prev modelid={modelid}")
        nmodel, pmodel, nname, pname = ModelsTable(DATABASE).get_next_prev(modelid)

        links = self.heading('models')
        page_dict = {'title': modelname, 'plaintitle':True, 'heading': self.config['title'], 'type':'model', 'navigation': links,
                    'nid':nmodel, 'pid':pmodel, 'next':nname, 'prev':pname, 'db':self.dbname, 'thisurl':f"/{self.dbname}/model/{modelid}"}

        return render_template("model_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts, 
                               hasvideos=hasvideos, viddicts=viddicts)

    def sites2(self): # 2
        """doesn't give the correct order, because select_group_by_order_by doesn't produce what I thought"""
        sites = {}
        for id,name,location in SitesTable(DATABASE).select_all():
            sites[id] = name
        photos = PhotosTable(DATABASE).select_group_by_order_by('site_id', 'id', 'desc')
        galldicts = []
        for _id, _model_id, site_id, _name, _location, _t, _count in photos:
            sitename = sites[site_id]
            try:
                thm = PhotosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
            galldicts.append({'href':f"/{self.dbname}/site/{site_id}", 'src':thumb, 'name':sitename, 'height':self.thumb_h})

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)
            
    def sites3(self): # 3
        """doesn't wotk becausemost_recent_photo expects a thumb column in route table"""
        sites = SitesTable(DATABASE).select_by_most_recent_photos('site_id')
        galldicts = []
        for site_id, sitename, location in sites:
            try:
                thm = PhotosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
            galldicts.append({'href':f"/{self.dbname}/site/{site_id}", 'src':thumb, 'name':sitename, 'height':self.thumb_h})

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)
            
    def sites(self): # 1
        """"""
        sites = SitesTable(DATABASE).select_all()

        hassites, galldicts = self.sitdict(sites)
        
        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 
                     'db':self.dbname, 'search': True}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)

    def site(self, siteid):
        """"""
        order = get_order("alpha")
        sitename = SitesTable(DATABASE).select_where('id', siteid)[0][1]
        photos = PhotosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
        videos = VideosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
    
        hasphotos, galldicts = self.galdict(photos, 'site', siteid)

        hasvideos, viddicts = self.viddict(videos, 'site', siteid)

        print(f"(site) get_next_prev siteid={siteid}")
        nsite, psite, nname, pname = SitesTable(DATABASE).get_next_prev(siteid)
    
        links = self.heading('sites')
        page_dict = {'title':sitename, 'plaintitle':True, 'heading': self.config['title'], 'type':'site', 
                     'navigation': links, 'nid':nsite, 'pid':psite, 'next':nname, 'prev':pname, 'db':self.dbname}

        return render_template("model_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts, 
                               hasvideos=hasvideos, viddicts=viddicts)

    def photos(self):
        """"""
        order = get_order("rlatest")
            
        if order == 'alpha':
            photos = PhotosTable(DATABASE).select_group_by_order_by('name', 'name', 'asc')
        elif order == 'ralpha':
            photos = PhotosTable(DATABASE).select_group_by_order_by('name', 'name', 'desc')
        elif order == 'rlatest': # or order == None or order in ("small", "large"):
            photos = PhotosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')
        elif order == 'latest':
            photos = PhotosTable(DATABASE).select_group_by_order_by('id', 'id', 'asc')
        elif order == 'pics':
            photos = PhotosTable(DATABASE).select_group_by_order_by('count', 'count', 'desc')
        elif order == 'rpics':
            photos = PhotosTable(DATABASE).select_group_by_order_by('count', 'count', 'asc')

        #if order == "2x":
        #    self.thumb_h = self.thumb_h * 1.6

        hasphotos, galldicts = self.galdict(photos)

        links = self.heading('photos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'photos', 'navigation': links, 
                     'db':self.dbname, 'search': True}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def videos(self):
        """"""
        order = get_order("alpha")
        
        videos = VideosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')

        #if order == "2x":
        #    self.thumb_h = self.thumb_h * 1.6
    
        hasvideos, viddicts = self.viddict(videos)

        links = self.heading('videos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'videos', 'navigation': links, 
                     'db':self.dbname, 'search': True}
        return render_template("videos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddicts=viddicts)


    def video(self, vid, sid=None, mid=None):
        """"""
        video = VideosTable(DATABASE).select_where('id', vid)[0]
        try:
            sql = f"select id, model_id, site_id, name, filename, thumb, poster, width, height, length from videos2 where id = {vid};"
            video2 = VideosTable(DATABASE).get_single_result(sql,10)
            print(video2)
        except OperationalError:
            video2 = [0,0,0,0,0,0,None]
        id, model_id, site_id, name, filename, thumb, width, height, length = video
        sitename = SitesTable(DATABASE).select_where('id', site_id)[0][1]
        try:
            modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''
        if DATABASE == 'flaskr/new_hegre.db':
            filename = filename.replace('.avi', '.mp4')

        if video2[6] is not None:
            poster = video2[6]
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{poster}"
        else:
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
        print(f"(video) get_next_prev vid={vid} site_id={sid}")
        if sid is not None: 
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'site_id', sid)
        print(f"(video) get_next_prev vid={vid} model_id {mid}")
        if mid is not None: 
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'model_id', mid)
        if mid is None and sid is None:
            nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid)
            

        links = self.heading('videos')
        prefix = ''
        if sid is not None: prefix+=f"site/{sid}/"
        if mid is not None: prefix+=f"model/{mid}/"
        
        titledict = {'site': {'href':f"/{self.dbname}/site/{site_id}", 'name':sitename}, 
                     'model':{'href':f"/{self.dbname}/model/{model_id}", 'name':modelname},
                     'folder':name}
        page_dict = {'title': titledict, 
                     'plaintitle':False, 'heading': self.config['title'], 'type':'video', 
                     'navigation': links, 'nid':nvideo, 'pid':pvideo, 'next':nname, 'prev':pname, 
                     'prefix':prefix, 'db':self.dbname}
        return render_template("video_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               viddict=viddict)


    def do_gallery(self, id, col, val, table, links):
        """"""
        pset = PhotosTable(DATABASE).select_where('id', id)[0]
        id, model_id, site_id, name, location, thumb, count = pset
        sitename = SitesTable(DATABASE).select_where('id', site_id)[0][1]
        try:
            modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''

        gallery = self.create_gallery(location, id, count)
        
        print(f"(do_gallery) get_next_prev pid={id} {col}={val}")
        next, prev, nname, pname = PhotosTable(DATABASE).get_next_prev(id, col, val)

        titledict = {'site': {'href':f"/{self.dbname}/site/{site_id}", 'name':sitename}, 
                     'model':{'href':f"/{self.dbname}/model/{model_id}", 'name':modelname},
                     'folder':name}
        prefix = ''
        if table is not None: prefix += table+'/'
        if val is not None: prefix += val+'/'
        
        page_dict = {'title':titledict, 'plaintitle':False, 'heading':self.config['title'], 'type':'gallery', 
                     'navigation':links, 'prefix':prefix, 'nid':next, 'pid':prev, 'next':nname, 'prev':pname, 
                     'db':self.dbname}

        return render_template("photo_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               gallpage=gallery,
                               hasedit=True, edit={'table':'photos', 'id':id})


    def old_create_gallery(self, fld, id, count):
        """relies on knowing the format of the image file name"""
        gall = []
        for i in range(count):
            n = i+1
            pic = os.path.basename(fld) 
            image = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{pic}_{n}.jpg"
            gall.append({'href':image, 'src':image})
        return gall


    def create_gallery(self, fld, id, count):
        """relies on being able to downloading the list of images from the gallery server"""
        # eg. self.config['webroot']/zdata/stuff.backup/sdc1/www.hegre-art.com/members//LubaAfterAShowerGen/
        
        gall = []
        url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/".replace(' ','%20')
        #print(f"{url}")
        st, out = unix(f"curl -s \"{url}\"")
        #print(f"{out}")
        for line in out.split('\n'):
            if line.find("[IMG]") > -1:
                img = line[line.find("href="):line.find("</a>")].split('"')[1]
                imgurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{img}"
                gall.append({'href':imgurl, 'src':imgurl, 'pic':img})
        return gall


    def search(self, term):
        """"""
        order = get_order("alpha")
        #term = get_search()

        sites = SitesTable(DATABASE).select_where_like('name', term)
        models = ModelsTable(DATABASE).select_where_like('name', term)
        photos = PhotosTable(DATABASE).select_where_like_group_order('name', term, 'id', 'id', 'desc')
        videos = VideosTable(DATABASE).select_where_like_group_order('name', term, 'id', 'id', 'desc')
        
        hasmodels, modeldicts = self.moddict(models)
        hasphotos, galldicts = self.galdict(photos)
        hasvideos, viddicts = self.viddict(videos)
        hassites, sitedicts = self.sitdict(sites)

        links = self.heading()
        page_dict = {'title':f"Search Results for '{term}'", 'plaintitle':True, 'heading': self.config['title'], 'type':'search', 
                     'navigation': links, 
                     'db':self.dbname, 'search': True}
        
        return render_template("search_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict, search_term=term,
                               hasphotos=hasphotos, galldicts=galldicts, 
                               hasmodels=hasmodels, modeldicts=modeldicts,
                               hassites=hassites, sitedicts=sitedicts, 
                               hasvideos=hasvideos, viddicts=viddicts)

    def random(self):
        """"""
        sites = SitesTable(DATABASE).select_all()
        models = ModelsTable(DATABASE).select_all()
        photos = PhotosTable(DATABASE).select_all()
        videos = VideosTable(DATABASE).select_all()

        models = random_selection(models, 8)
        photos = random_selection(photos, 8)
        videos = random_selection(videos, 4)

        hasmodels, modeldicts = self.moddict(models)
        hasphotos, galldicts = self.galdict(photos)
        hasvideos, viddicts = self.viddict(videos)
        #hassites, sitedicts = self.sitdict(sites)

        links = self.heading()
        page_dict = {'title':'Random Selection', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 
                     'navigation': links, 
                     'db':self.dbname, 'search': True}
        
        return render_template("search_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict, #search_term=s,
                               hasphotos=hasphotos, galldicts=galldicts, 
                               hasmodels=hasmodels, modeldicts=modeldicts,
                               hassites=False, #sitedicts=sitedicts, 
                               hasvideos=hasvideos, viddicts=viddicts,
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
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'button_class':'fourbuttons'}
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
