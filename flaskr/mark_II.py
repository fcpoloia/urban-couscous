#!/usr/bin/env python3

# Mark II verion of the website using a different database schema

from flask import Flask, render_template
import glob, os

from flaskr.db2 import ConfigTable, ModelsTable, SitesTable, PhotosTable, VideosTable

DATABASE = "flaskr/new_kindgirls.db"

class SiteDB:
    def __init__(self, dbname):
        self.dbname = dbname

def get_config(dbname):
    global DATABASE
    DATABASE = f"flaskr/new_{dbname}.db"
    
    val = ConfigTable(DATABASE).select_all()[0]
    try:
        config = {'id':val[0], 'rootpath':val[1], 'title':val[2], 
              'images':val[3], 'thumbs':val[4], 'videos':val[5] }
    except:
        print(val)
        raise
    config['models'] = 'html'
    if dbname == "hegre":
        config['models'] = 'updates/models/'
    return config

        
class HtmlSite:
    def __init__(self, dbname):
        """"""
        self.dbname = dbname
        self.config = get_config(dbname)
        self.thumb_h = 160
        if dbname == "inthecrack":
            self.thumbs0 = ".pics"
        elif dbname == "hegre":
            self.thumbs0 = ''
        else:
            self.thumbs0 = "0.thumbs"

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

    def models(self, letter=''):
        """"""
        #models = ModelsTable(DATABASE).select_order_by('id', 'desc')
        models = ModelsTable(DATABASE).select_by_most_recent_photos('model_id')
    
        galldicts = []
        for id,name,thumb,_ in models:
            thumburl = f"http://gallery{self.config['rootpath']}/{self.config['models']}{thumb}"
            #if self.dbname == "inthecrack":
            #    thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            if letter.isalpha():
                if model.lower().startswith(letter.lower()):
                    galldicts.append({'href':f"/{self.dbname}/model/{model}", 'src':thumburl, 'name':name, 'height':self.thumb_h})
            else:
                #galldicts.append({'href':f"/{self.dbname}/model/{model}", 'src':thumb, 'name':model, 'height':self.thumb_h})
                galldicts.append({'href':f"/{self.dbname}/model/{id}", 'src':thumburl, 'name':name, 'height':self.thumb_h})

        links = self.heading('models')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)

    def model(self, modelid, letter=''):
        """"""
        photos = PhotosTable(DATABASE).select_where('model_id',modelid)
        videos = VideosTable(DATABASE).select_where('model_id',modelid)
        modelname = ModelsTable(DATABASE).select_where('id',modelid)[0][1]
    
        galldicts = []
        for gallery in photos:
            id, model_id, site_id, name, location, thumb, count = gallery
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thumb}"
            #if self.dbname == "inthecrack":
            #    thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/model/{modelid}/{id}", 'src':thumb, 'height':self.thumb_h, 'name': name})

        hasvideos = False
        viddicts = []
        if len(videos) > 0:
            hasvideos = True
            for vid in videos:
                id, model_id, site_id, name, filename, thumb, width, height, length = vid
                thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
                #video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{name}"
                viddicts.append({'href':f"/{self.dbname}/video/model/{modelid}/{id}", 'src':thumb_url, 'height':self.thumb_h, 'name': name})
    
        # next/prev needs to follow sort order of models page above
        nmodel, pmodel, nname, pname = ModelsTable(DATABASE).get_next_prev(modelid)

        links = self.heading('models')
        page_dict = {'title': modelname, 'plaintitle':True, 'heading': self.config['title'], 'type':'model', 'navigation': links,
                    'nid':nmodel, 'pid':pmodel, 'next':nname, 'prev':pname, 'db':self.dbname}

        return render_template("model_page.html", 
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
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thm}"
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
            galldicts.append({'href':f"/{self.dbname}/site/{site_id}", 'src':thumb, 'name':sitename, 'height':self.thumb_h})

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)
            
    def sites3(self): # 3
        """doesn't wotk becausemost_recent_photo expects a thumb column in route table"""
        sites = SitesTable(DATABASE).select_by_most_recent_photos('site_id')
        galldicts = []
        for site_id, sitename, location, photo_id in sites:
            try:
                thm = PhotosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thm}"
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', site_id, 'id', 'desc')[0][5]
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
            galldicts.append({'href':f"/{self.dbname}/site/{site_id}", 'src':thumb, 'name':sitename, 'height':self.thumb_h})

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)
            
    def sites(self): # 1
        """"""
        sites = SitesTable(DATABASE).select_all()
        ordered_sites = {}
        galldicts = []
        for id,name,location in sites[:1000]:
            try:
                pid,_,_,_,_,thm = PhotosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][:6]
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
            except IndexError:
                vname = VideosTable(DATABASE).select_where_order_by('site_id', id, 'id', 'desc')[0][5]
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/{self.dbname}/site/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h}
            #if self.dbname == "inthecrack":
            #    thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
        photo_ids = [k for k in ordered_sites]
        photo_ids.sort()
        photo_ids.reverse()
        for pid in photo_ids:
            galldicts.append(ordered_sites[pid])

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)

    def site(self, siteid):
        """"""
        sitename = SitesTable(DATABASE).select_where('id', siteid)[0][1]
        galleries = PhotosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
        videos = VideosTable(DATABASE).select_where_group_by_order_by('site_id', siteid, 'id', 'id', 'desc')
    
        galldicts = []
        for gallery in galleries[:1000]:
            id, model_id, site_id, name, location, thumb, count = gallery
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thumb}"
            #if self.dbname == "inthecrack":
            #    thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/site/{siteid}/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h})

        hasvideos = False
        viddicts = []
        if len(videos) > 0:
            hasvideos = True
            for vid in videos:
                id, model_id, site_id, name, filename, thumb, width, height, length = vid
                thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
                video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{name}"
                viddicts.append({'href':f"/{self.dbname}/video/site/{site_id}/{id}", 'src':thumb_url, 'height':self.thumb_h, 'name': name})

        nsite, psite, nname, pname = SitesTable(DATABASE).get_next_prev(siteid)
    
        links = self.heading('sites')
        page_dict = {'title':sitename, 'plaintitle':True, 'heading': self.config['title'], 'type':'site', 
                     'navigation': links, 'nid':nsite, 'pid':psite, 'next':nname, 'prev':pname, 'db':self.dbname}

        return render_template("model_page.html", 
                               page=page_dict,
                               galldicts=galldicts, 
                               hasvideos=hasvideos, viddicts=viddicts)


    def photos(self):
        """"""
        photos = PhotosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')

        galldicts = []
        for gallery in photos[:1000]:
            id, model_id, site_id, name, location, thumb, count = gallery
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{thumb}"
            #if self.dbname == "inthecrack":
            #    thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h})

        links = self.heading('photos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 
                     'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)


    def videos(self):
        """"""
        videos = VideosTable(DATABASE).select_group_by_order_by('id', 'id', 'desc')
    
        galldicts = []
        for vid in videos[:1000]:
            id, model_id, site_id, name, filename, thumb, width, height, length = vid
            thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            galldicts.append({'href':f"/{self.dbname}/video/{id}", 'src':thumb_url, 'name':name, 'height':self.thumb_h})

        links = self.heading('videos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 
                     'db':self.dbname}
        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)


    def video(self, vid, sid=None, mid=None):
        """"""
        video = VideosTable(DATABASE).select_where('id', vid)[0]
    
        id, model_id, site_id, name, filename, thumb, width, height, length = video
        modelname = ModelsTable(DATABASE).select_where('id', model_id)[0][1]
        if DATABASE == 'flaskr/new_hegre.db':
            filename = filename.replace('.avi', '.mp4')
        thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
        video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{filename}"
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
        
        page_dict = {'title':f"{modelname}", 'plaintitle':True, 'heading': self.config['title'], 'type':'video', 
                     'navigation': links, 'nid':nvideo, 'pid':pvideo, 'next':nname, 'prev':pname, 
                     'prefix':prefix, 'db':self.dbname}
        return render_template("video_page.html", 
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

        #print(val,prev,next)
    
        #links = self.heading('photos')

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
                               page=page_dict,
                               gallpage=gallery)


    def create_gallery(self, fld, id, count):
        """"""
        gall = []
        for i in range(count):
            n = i+1
            pic = os.path.basename(fld) 
            image = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{fld}/{pic}_{n}.jpg"
            #if self.dbname == "inthecrack":
            #    image = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{fld}/{id}_%03d.jpg" % n
            gall.append({'href':image, 'src':image})
        return gall


