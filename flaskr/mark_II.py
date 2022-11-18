#!/usr/bin/env python3

# Mark II verion of the website using a different database schema

from flask import Flask, render_template
import glob, os
from subprocess import getstatusoutput as unix

from flaskr.db2 import ConfigTable, ModelsTable, SitesTable, PhotosTable, VideosTable

DATABASE = "flaskr/new_kindgirls.db"

class SiteDB:
    def __init__(self, dbname):
        self.dbname = dbname

def get_config(dbname):
    global DATABASE
    DATABASE = f"flaskr/new_{dbname}.db"
    #print(DATABASE)
    vals = ConfigTable(DATABASE).select_all()[0]
    cols = ConfigTable(DATABASE).column_list()
    config = {}
    if len(vals) == len(cols):
        for i in range(len(cols)):
            config[cols[i]] = vals[i]
    #print(config)
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
        #print(dbname)
        self.dbname = dbname
        self.config = get_config(dbname)
        self.thumb_h = 160

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


    def moddict(self, models):
        """"""
        mdicts = []
        for id,name,thumb in models:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href':f"/{self.dbname}/model/{id}", 'src':thumburl, 'name':name, 'height':self.thumb_h})
        return (len(models) > 0), mdicts


    def galdict(self, photos):
        """"""
        gdict = []
        for gallery in photos[:1000]:
            id, model_id, site_id, name, location, thumb, count = gallery
            thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thumb}"
            name = name.replace('_', ' ')[:50]
            gdict.append({'href':f"/{self.dbname}/gallery/model/{model_id}/{id}", 'src':thumb, 'height':self.thumb_h, 'name': name})
        return (len(photos) > 0), gdict


    def viddict(self, videos):
        """"""
        vdicts = []
        for vid in videos:
            id, model_id, site_id, name, filename, thumb, width, height, length = vid
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            vdicts.append({'href':f"/{self.dbname}/video/{id}", 'src':thumb_url, 'name':name, 'theight':self.thumb_h, 
                             'w': width, 'h': height, 'mlen':human_time(length)})
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
        models = ModelsTable(DATABASE).select_by_most_recent_photos('model_id')
        if len(models) == 0:
            models = ModelsTable(DATABASE).select_order_by('id', 'desc')
        
        hasmodels, galldicts = self.moddict(models)
        
        links = self.heading('models')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 
                     'db':self.dbname, 'search': True}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)

    def model(self, modelid):
        """"""
        photos = PhotosTable(DATABASE).select_where('model_id',modelid)
        videos = VideosTable(DATABASE).select_where('model_id',modelid)
        modelname = ModelsTable(DATABASE).select_where('id',modelid)[0][1]
    
        hasphotos, galldicts = self.galdict(photos)

        hasvideos, viddicts = self.viddict(videos)
    
        # next/prev needs to follow sort order of models page above
        nmodel, pmodel, nname, pname = ModelsTable(DATABASE).get_next_prev(modelid)

        links = self.heading('models')
        page_dict = {'title': modelname, 'plaintitle':True, 'heading': self.config['title'], 'type':'model', 'navigation': links,
                    'nid':nmodel, 'pid':pmodel, 'next':nname, 'prev':pname, 'db':self.dbname}

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
        sitename = SitesTable(DATABASE).select_where('id', siteid)[0][1]
        photos = PhotosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
        videos = VideosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
    
        hasphotos, galldicts = self.galdict(photos)

        hasvideos, viddicts = self.viddict(videos)

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
        photos = PhotosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')

        hasphotos, galldicts = self.galdict(photos)

        links = self.heading('photos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 
                     'db':self.dbname, 'search': True}

        return render_template("photos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def videos(self):
        """"""
        videos = VideosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')
    
        hasvideos, galldicts = self.viddict(videos)

        links = self.heading('videos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 
                     'db':self.dbname, 'search': True}
        return render_template("videos.html", 
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts)


    def video(self, vid, sid=None, mid=None):
        """"""
        video = VideosTable(DATABASE).select_where('id', vid)[0]
    
        id, model_id, site_id, name, filename, thumb, width, height, length = video
        sitename = SitesTable(DATABASE).select_where('id', site_id)[0][1]
        try:
            modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
        except IndexError:
            modelname = ''
        if DATABASE == 'flaskr/new_hegre.db':
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
        if sid is not None: nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'site_id', sid)
        if mid is not None: nvideo, pvideo, nname, pname = VideosTable(DATABASE).get_next_prev(vid, 'model_id', mid)

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

        if DATABASE == 'flaskr/new_hegre.db':
            location = name
        gallery = self.create_gallery(location, id, count)
        
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
                               gallpage=gallery)


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
        url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/"
        st, out = unix(f"curl -s {url}")
        for line in out.split('\n'):
            if line.find("[IMG]") > -1:
                img = line[line.find("href="):line.find("</a>")].split('"')[1]
                imgurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{img}"
                gall.append({'href':imgurl, 'src':imgurl})
        return gall


    def search(self, s):
        """"""
        sites = SitesTable(DATABASE).select_where_like('name', s)
        models = ModelsTable(DATABASE).select_where_like('name', s)
        photos = PhotosTable(DATABASE).select_where_like('name', s)
        videos = VideosTable(DATABASE).select_where_like('name', s)
        
        hasmodels, modeldicts = self.moddict(models)
        hasphotos, galldicts = self.galdict(photos)
        hasvideos, viddicts = self.viddict(videos)
        hassites, sitedicts = self.sitdict(sites)

        links = self.heading()
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 
                     'navigation': links, 
                     'db':self.dbname, 'search': True}
        
        return render_template("search_page.html", 
                               webroot=self.config['webroot'],
                               page=page_dict, search_term=s,
                               hasphotos=hasphotos, galldicts=galldicts, 
                               hasmodels=hasmodels, modeldicts=modeldicts,
                               hassites=hassites, sitedicts=sitedicts, 
                               hasvideos=hasvideos, viddicts=viddicts)

