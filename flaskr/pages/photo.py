
from subprocess import getstatusoutput as unix

from flask import render_template, session
from flask.views import View

from flaskr.pages.base import HtmlSite, PageInfo, PageBuilder, do_post_get
from flaskr.pages.sorttypes import sorting


#@app.route("/<dbname>/gallery/site/<sid>/<pid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/gallery/model/<mid>/<pid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/gallery/<page>/<pageid>/<photoid>", methods=['POST', 'GET'])
#def gallery_page_id_id(dbname, page, pageid, photoid):
#    """"""
#    do_post_get()
#    print(f"route gallery_page_id_id {photoid}")
#    mysite = dbpage_factory('gallery',dbname)
#    links = mysite.heading(page+'s')
#    return mysite.do_gallery(photoid, page+'_id', pageid, page, links)

class GalleryPageView(View):
    methods = ["POST", "GET"]

    def __init__(self, a):
        self.appt = a

    def dispatch_request(self, dbname, page, pageid, photoid):
        do_post_get()
        self.appt.logger.info(f"route gallery_page_id_id {photoid}")
        mysite = HtmlPhotoSetPage(dbname)
        links = mysite.heading(page+'s')
        return mysite.do_gallery(photoid, page+'_id', pageid, page, links)


#@app.route("/<dbname>/gallery/<idx>", methods=['POST', 'GET'])
#def gallery(dbname, idx):
#    """"""
#    do_post_get()
#    print(f"route dbname gallery {idx}")
#    mysite = dbpage_factory('gallery',dbname)
#    links = mysite.heading('photos')
#    return mysite.do_gallery(idx, None, None, None, links)

class GalleryIdxPageView(View):
    methods = ["POST", "GET"]

    def __init__(self, a):
        self.appt = a

    def dispatch_request(self, dbname, idx): #page, pageid=None, photoid=None):
        do_post_get()
        self.appt.logger.info(f"route dbname gallery {idx}")
        mysite = HtmlPhotoSetPage(dbname)
        links = mysite.heading('photos')
        return mysite.do_gallery(idx, None, None, None, links)



class HtmlPhotoSetPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self.dbname = dbname


    def get_columns(self, count):
        """"""
        use_thms = True
        columns = 12
        if 'imagesize' in session and session['imagesize'] == 'large':
            use_thms = False
            columns = 0
        elif count < 25:
            use_thms = False
            columns = 2
        print(f"get_columns - {columns} {use_thms}")
        return (columns, use_thms)


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

        idx, _model_id, site_id, name, location, _thumb, count, _pdate = psets[0]

        sitename = self.db.sites_table().select_where('id', site_id)[0][1]
        #try:
        #    modelname = self.db.models_table().select_where('id', model_id)[0][1]
        #except IndexError:
        #    modelname = ''

        columns, use_thms = self.get_columns(count)
        gallery = self.create_gallery(location, idx, count, use_thms)
        #print(f"gallery len {len(gallery)} count {count}")
        #if count < 25:
        #    gallery = self.create_gallery(location, idx, count, False)
        #else:
        #    gallery = self.create_gallery(location, idx, count, True)

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

        page_dict['columns'] = columns
        #if count < 25:
        #    page_dict['columns'] = 2
        #else:
        #    page_dict['columns'] = 12
        print(f"photo_page.html {idx} pd[cols]={page_dict['columns']} cols={columns}")
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
            #print(line)
            if line.find("[IMG]") > -1:
                img = line[line.find("href="):line.find("</a>")].split('"')[1]
                imgurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/{img}"
                picurl = imgurl
                if use_thms:
                    print(self.dbname)
                    #if self.dbname != "femjoy":
                    picurlimg = img.replace('jpg','png').replace('&amp;','&')
                    #else:
                    #    picurlimg = img.replace('&amp;','&')
                    picurl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{fld}/.pics/{picurlimg}"
                    print(picurl)
                gall.append({'href': imgurl,
                             'src': picurl,
                             'pic': img}
                             )
        if len(gall) == 0:
            print(f"{url} - {st} {out}")
        return gall



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

