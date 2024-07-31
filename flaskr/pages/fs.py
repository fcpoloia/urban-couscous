
import os
import glob
from html.entities import html5
#from markupsafe import escape

from flask import request, render_template, session, current_app, url_for
from flask.views import View

from flaskr.pages.base import HtmlSite


# -----------------------------------------------------------------------------
# To Do:
# - custom default sorting
# - use of Sort menu items
# - support the search field
# Done - read .ignore file and support .latest and .reverse
# - read comments and movie_dims files
# - implement paging (max 500 items)
# - add a 'show hidden files' option and add more file types to the ignore/hidden list
# - videos should point to a videos page ?
# Done - need to change css for plain files and non-logo folders when mixed with images
# Done - remove the Random button
# - deal with Permission Denied errors
#
# -----------------------------------------------------------------------------


# @app.route("/fs/<page:subpage>")
# @app.route("/fs")

class FileSystemView(View):
    methods = ["POST", "GET"]

    def __init__(self, root=None):
        """"""
        self.root = True

    def dispatch_request(self, subpath='/'):
        """"""
        mysite = HtmlFileSystem()
        return mysite.fs(subpath)


class HtmlFileSystem(HtmlSite):
    """replicates the old phpgallery site"""

    def __init__(self):
        """"""
        super().__init__()
        self.rpath=''
        self.wpath=''

    def magic(self, item):
        """item is image or movie or not"""
        exten = os.path.splitext(item)[1].lower()
        if exten in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        if exten in ['.mp4', '.mkv']:
            return 'movie'
        return ''

    def shorter(self, path, slen=25):
        """return the start of the path"""
        return path[:slen]+html5["hellip;"] if len(path) > slen else  path

    def tail(self, path, slen=150):
        """return the end of the path"""
        return html5["hellip;"]+path[-slen:] if len(path) > slen else  path

    def escape(self, str):
        """"""
        return str.replace('#', '%23')

    def fs(self, path):
        """main method"""
        if path == '/':
            path=''
        self.rpath = path if path.startswith('/') else f"/{path}".replace('//','/')
        self.wpath = "http://"+request.host.replace(':5000','')+'/'+path+'/'
        upath = os.path.dirname('/'+path)
        wupath = upath

        filelist = FileList(self.rpath)

        # navigation, up, next, prev

        if wupath == '/':
            wupath=''

        n=p=''
        nr=pr="noanchor"
        dirlist = sorted([d for d in os.listdir(upath) if os.path.isdir(os.path.join(upath,d))])
        for c in range(len(dirlist)):
            if dirlist[c] == os.path.basename('/'+path):
                if c > 0:
                    p = dirlist[c-1]
                    pr=""
                if c < len(dirlist)-1:
                    n = dirlist[c+1]
                    nr=""

        links = {
            "up": {"href": f"/fs{wupath}", "title": "Up", 'class':'', 'rows': 1 },
            "prev": {"href": f"/fs{wupath}/{p}", "title": "Prev", 'class':pr, 'rows': 1 },
            "next": {"href": f"/fs{wupath}/{n}", "title": "Next", 'class':nr, 'rows': 1 },
        }

        listing=[]
        comments=self.rpath+" "

        # add directories first

        for item in filelist.get_dirs():
            if os.path.isdir(os.path.join(self.rpath, item)): # needs thumbnails on folders
                bitem = os.path.basename(item)
                if item in filelist.logo:
                    listing.append({'kind': 'logo', 'name': item, 'basename': bitem, 'height':'180px', 'href': "http://"+request.host+'/fs'+'/'+self.escape(item), 'src': self.wpath+filelist.logo[item]})
                else:
                    listing.append({'kind': 'dir',  'name': self.shorter(item, 90), 'basename': bitem, 'href': "http://"+request.host+'/fs'+'/'+self.escape(item)})

        # add files next

        for item in filelist.get_files():

            bitem = os.path.basename(item)

            # check for movies, images, pdf
            if self.magic(bitem) == 'image': # needs basename, height
                #current_app.logger.info(f"{os.path.exists(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.png')} - {self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.png'}")
                if os.path.exists(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.png'):
                    src = self.wpath+'.pics/'+self.escape(os.path.splitext(bitem)[0]+'.png')
                    #logger.info(src)
                elif os.path.exists(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.jpg'):
                    src = self.wpath+'.pics/'+self.escape(os.path.splitext(bitem)[0]+'.jpg')
                    #logger.info(src)
                else:
                    src = self.wpath+self.escape(bitem)
                    #logger.info(src)
                listing.append({'kind': 'image', 'name': item, 'basename': self.escape(bitem), 'height': '200px', 'href': self.wpath+self.escape(bitem), 'src': src})

            elif self.magic(bitem) == 'movie': # needs h, w, mlen
                src=url_for("static", filename="movie-blank-512.png") #'w':'209', 'h':'224'
                ht=240
                wt=224
                movie_kind = 'movie_icon'
                if os.path.exists(os.path.join(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.png')):
                    src = os.path.join(self.wpath+'.pics/'+os.path.splitext(bitem)[0]+'.png')
                    movie_kind = 'movie'
                elif os.path.exists(os.path.join(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+'.thm')):
                    src = os.path.join(self.wpath+'.pics/'+os.path.splitext(bitem)[0]+'.thm')
                    movie_kind = 'movie'
                listing.append({'kind': movie_kind, 'name': item, 'basename': bitem, 'href': self.wpath+bitem, 'src': src, 'height':f"{ht}px", 'width':f"{wt}px"})

            else:
                listing.append({'kind': 'file', 'name':item, 'basename': self.shorter(bitem, 90), 'href': self.wpath+bitem, 'src':url_for("static",filename="file-blank-512.png")})

        # title plaintitle heading type | navigation db
        page_dict = {
            'title': f"{self.tail(path,100)} ({len(listing)} items)",
            'pagetitle': os.path.basename(self.rpath),
            'heading': 'phpgallery',
            'plaintitle':True,
            'button_class':'fivebuttons',
            'navigation':links,
            'type':'fs',
        }

        return render_template("fs.html", webroot="http://"+request.host.replace(':5000',''),
                                page=page_dict, listing=listing, comments=comments)


class FileList:
    """"""
    def __init__(self, path):
        """"""
        self.path = path
        self.fullfilelist = [os.path.join(path,d) for d in os.listdir(path)]
        self.ignorelist = self.load_ignore()
        self.logo = self.load_logo()

    def get_dirs(self):
        """"""
        filelist = self.sort([d for d in self.fullfilelist if os.path.isdir(d) and not self.ignored(os.path.basename(d))])
        return filelist

    def get_files(self):
        """"""
        filelist = self.sort([d for d in self.fullfilelist if not os.path.isdir(d) and not self.ignored(os.path.basename(d))])
        return filelist

    def sort(self, items):
        """"""
        latest = os.path.exists(os.path.join(self.path,'.latest'))
        revers = os.path.exists(os.path.join(self.path,'.reverse'))

        if latest: # date order most recent first
            list_of_files = sorted(items, key = os.path.getmtime, reverse=True)

        else: #if self.get_order in ['alpha','ralpha']:
            list_of_files = sorted(items)

        if revers: #self.get_order().startswith('r'):
            list_of_files.reverse()
        return list_of_files

    def ignored(self, item, show_hidden=False):
        """is item ignored"""
        return item.startswith('.') or item in self.ignorelist

    def load_ignore(self):
        """import the .ignore file"""
        ignores = ['.ignore', 'comments', 'comments.php', 'movie_dims']
        if os.path.exists(os.path.join(self.path, '.ignore')):
            with open(os.path.join(self.path, '.ignore'), 'r') as fp:
                ignores = ignores + fp.readlines()
        return ignores

    def load_logo(self):
        """import the .logo file"""
        logo={}
        if os.path.exists(os.path.join(self.path, '.logo')):
            with open(os.path.join(self.path, '.logo'), 'r') as fp:
                lines = fp.readlines()
                for line in lines:
                    d, p = line.split(',')[:2]
                    logo[d] = p
        return logo

    def get_order(self):
        """"""
        if 'order' in session:
            order = session['order']
        else:
            order = 'alpha'
        return order

