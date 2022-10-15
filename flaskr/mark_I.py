#!/usr/bin/env python3

# Mark I verion of the website

"""
- get sites needs next prev site 
- get site galleries needs next prev within the site
- need a models page
- need a model galleries page with next prev withing the model
- needs a videos page
- create links on gallery pages for model and site
create links on model pages for site
create form for editing model-name associated to gallery (try floating css block)
add search/filter options - (model-name, site, first letter)
add sort order options = (alpha-numeric, id, latest)
sites page = sort by ( number of sets, alpha-numeric, latest photo set )
models page - sort by ( number of sets, alpha-numeric, latest photo set )
limit page length and add next/prev page feature
need an up link to
- need to distinguish between title (on browser) and title (on page)
- need to sort out proper templating of html and css

refactor code below
"""

from flask import render_template
import glob, os

from flaskr.getkindgirls_sql import GirlsDB


class SiteDB:
    """wrapper class to isolate GirlsDB class"""

    def __init__(self, dbname):
        self.kdb = GirlsDB()
        self.kdb.connectdb(f"flaskr/{dbname}.db")

    def dereference(self, id):
        _id, location = self.kdb.get_id(id)
        return location
        
    def get_pset(self, id):
        return self.kdb.get_photoset(id)

    def get_np_id(self, id, column=None, value=None):
        """pid, nid"""
        return self.kdb.get_next_prev_id(id, column, value)

    def get_np_site(self, site, column=None, value=None):
        """psite, nsite"""
        return self.kdb.get_next_prev_site(site, column, value)

    def get_np_model(self, model, column=None, value=None):
        """psite, nsite"""
        return self.kdb.get_next_prev_model(model, column, value)

    def get_np_video(self, video, column=None, value=None):
        """pvideo, nvideo"""
        return self.kdb.get_next_prev_video(video, column, value)

    def get_all_sites(self):
        return self.kdb.get_sites()

    def get_all_models(self):
        return self.kdb.get_models_sort_by_set_count()

    def get_all_photos(self):
        return self.kdb.get_photos()

    def get_site_galleries(self, site):
        return self.kdb.get_site_galleries(site)

    def get_model_galleries(self, model):
        return self.kdb.get_model_galleries(model)

    def get_img_count(self, id):
        return int(self.kdb.get_image_count(id))

    def get_all_videos(self):
        return self.kdb.get_all_videos()

    def get_model_videos(self, model):
        return self.kdb.get_model_videos(model)

    def get_video(self, vid):
        return self.kdb.get_video(vid)

    def get_config(self):
        val = self.kdb.get_config()
        config = {'id':val[0], 'rootpath':val[1], 'title':val[2], 
                  'images':val[3], 'thumbs':val[4], 'videos':val[5] }
        return config


class HtmlSite:
    def __init__(self, dbname):
        """"""
        #self.app = app
        self.mysite = SiteDB(dbname)
        self.dbname = dbname
        self.config = self.mysite.get_config()
        self.thumb_h = 160
        if dbname == "inthecrack":
            self.thumbs0 = ".pics"
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
        models = self.mysite.get_all_models()
    
        galldicts = []
        for id,model,name,location in models:
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{name}_1.jpg"
            if self.dbname == "inthecrack":
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            if letter.isalpha():
                if model.lower().startswith(letter.lower()):
                    galldicts.append({'href':f"/{self.dbname}/model/{model}", 'src':thumb, 'name':model, 'height':self.thumb_h})
            else:
                galldicts.append({'href':f"/{self.dbname}/model/{model}", 'src':thumb, 'name':model, 'height':self.thumb_h})

        links = self.heading('models')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)

    def model(self, model, letter=''):
        """"""
        galleries = self.mysite.get_model_galleries(model)
        videos = self.mysite.get_model_videos(model)
    
        galldicts = []
        for gallery in galleries:
            id, name, location = gallery
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{name}_1.jpg"
            if self.dbname == "inthecrack":
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/{model}/{id}", 'src':thumb, 'height':self.thumb_h, 'name': name})

        hasvideos = False
        viddicts = []
        if len(videos) > 0:
            hasvideos = True
            for vid in videos:
                id, name, location, thumb, width, height, length, model, site = vid
                thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
                video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{name}"
                viddicts.append({'href':f"/{self.dbname}/video/{id}", 'src':thumb_url, 'height':self.thumb_h, 'name': name})
    
        #models = mysite.get_all_models()
        #c = 0
        #for i,m,n in models:
        #    if model == m:
        #        break
        #    c+=1
        #nmodel = pmodel = None
        #if c < len(models)-1: nmodel = models[c+1][1]
        #if c > 0: pmodel = models[c-1][1]

        #pmodel, nmodel = mysite.get_np_model(model)#, 'model', model)
    
        #prev_str = next_str = ""
        #if pmodel is not None:
        #    prev_str = f"[{pmodel}]"
        #if nmodel is not None:
        #    next_str = f"[{nmodel}]"

        links = self.heading('models')
        page_dict = {'title': model, 'plaintitle':True, 'heading': self.config['title'], 'type':'model', 'navigation': links,
                    # 'next':nmodel, 'next_str':next_str, 'prev':pmodel, 'prev_str':prev_str
                    'db':self.dbname}

        return render_template("model_page.html", 
                               page=page_dict,
                               galldicts=galldicts, 
                               hasvideos=hasvideos, viddicts=viddicts)

    def sites(self):
        """"""
        sites = self.mysite.get_all_sites()
    
        galldicts = []
        for id,site,name,location in sites[:1000]:
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{name}_1.jpg"
            if self.dbname == "inthecrack":
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/site/{site}", 'src':thumb, 'name':site, 'height':self.thumb_h})

        links = self.heading('sites')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)

    def site(self, site):
        """"""
        galleries = self.mysite.get_site_galleries(site)
    
        galldicts = []
        for gallery in galleries[:1000]:
            id, name, location = gallery
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{name}_1.jpg"
            if self.dbname == "inthecrack":
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/{site}/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h})

        psite, nsite = self.mysite.get_np_site(site)
    
        links = self.heading('sites')
        page_dict = {'title':site, 'plaintitle':True, 'heading': self.config['title'], 'type':'site', 
                     'navigation': links, 'next':nsite, 'prev':psite, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)


    def photos(self):
        """"""
        photos = self.mysite.get_all_photos()

        galldicts = []
        for id,name,location in photos[:1000]:
            thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{self.thumbs0}/{name}_1.jpg"
            if self.dbname == "inthecrack":
                thumb = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{location}/{self.thumbs0}/{id}_001.jpg"
            galldicts.append({'href':f"/{self.dbname}/gallery/{id}", 'src':thumb, 'name':name, 'height':self.thumb_h})

        links = self.heading('photos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 'db':self.dbname}

        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)


    def videos(self):
        """"""
        videos = self.mysite.get_all_videos()
    
        galldicts = []
        for vid in videos[:1000]:
            id, name, location, thumb, width, height, length, model, site = vid
            thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{name}"
            galldicts.append({'href':f"/{self.dbname}/video/{id}", 'src':thumb_url, 'name':name, 'height':self.thumb_h})

        links = self.heading('videos')
        page_dict = {'title':'', 'plaintitle':True, 'heading': self.config['title'], 'type':'', 'navigation': links, 'db':self.dbname}
        return render_template("photos.html", 
                               page=page_dict,
                               galldicts=galldicts)


    def video(self, vid):
        """"""
        video = self.mysite.get_video(vid)
    
        id, name, location, thumb, width, height, length, model, site = video

        thumb_url = f"http://gallery{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
        video_url = f"http://gallery{self.config['rootpath']}/{self.config['videos']}/{name}"
        if int(width) > 1280 or int(height) > 720:
            width=1280
            height=720

        viddict = {'height':height, 'width':width, 'thumb_url':thumb_url, 'video_url':video_url}

        # need a next_prev_video call
        pvideo, nvideo = self.mysite.get_np_video(vid)

        links = self.heading('videos')
        page_dict = {'title':f"{model}", 'plaintitle':True, 'heading': self.config['title'], 'type':'video', 
                     'navigation': links, 'next':nvideo, 'prev':pvideo, 'db':self.dbname}
        return render_template("video_page.html", 
                               page=page_dict,
                               viddict=viddict)


    def do_gallery(self, id, col, val, links):
        """"""
        id, name, folder, site, model, count = self.mysite.get_pset(id)
        if folder != None:
            gallery = self.create_gallery(folder, id, count)
        
        prev, next = self.mysite.get_np_id(id, col, val)

        print(val,prev,next)
        if val is not None:
            next=f"{val}/{next}" 
            prev=f"{val}/{prev}" 
    
        links = self.heading('photos')

        titledict = {'site': {'href':f"/{self.dbname}/site/{site}", 'name':site}, 
                     'model':{'href':f"/{self.dbname}/model/{model}", 'name':model},
                     'folder':name}

        page_dict = {'title':titledict, 'plaintitle':False, 'heading':self.config['title'], 'type':'gallery', 
                     'navigation':links, 'next':next, 'prev':prev, 'db':self.dbname}

        return render_template("photo_page.html", 
                               page=page_dict,
                               gallpage=gallery)


    def create_gallery(self, fld, id, count):
        """"""
        urls = glob.glob(f"{self.config['images']}/{fld}/*.jpg")

        urls.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        files = urls
        gall = []
        for i in range(count):
            n = i+1
            pic = os.path.basename(fld) 
            image = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{fld}/{pic}_{n}.jpg"
            if self.dbname == "inthecrack":
                image = f"http://gallery{self.config['rootpath']}/{self.config['images']}/{fld}/{id}_%03d.jpg" % n
            gall.append({'href':image, 'src':image})
        return gall



#def create_app(test_config=None):
#    """"""
#    app = Flask(__name__)
#    from flaskr.getkindgirls_sql import KindgirlsDB
#    site = HtmlSite(KindgirlsDB())
#    return app


#if __name__ == '__main__':
#    app.run(host="0.0.0.0", port=8181)

