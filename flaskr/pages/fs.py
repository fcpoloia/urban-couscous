
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring
# pylint: disable-msg=invalid-name

import os
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

THM_HT="200px"

class FileSystemView(View):
    methods = ["POST", "GET"]

    def __init__(self):
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
        self.movie_kind = 'movie_icon'
        self.filelist=None
        self.listing=[]

    def magic(self, item):
        """item is image or movie or not"""
        exten = os.path.splitext(item)[1].lower()
        if exten in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        if exten in ['.mp4', '.mkv']:
            return 'movie'
        return 'file'

    def shorter(self, path, slen=25):
        """return the start of the path"""
        return path[:slen]+html5["hellip;"] if len(path) > slen else  path

    def tail(self, path, slen=150):
        """return the end of the path"""
        return html5["hellip;"]+path[-slen:] if len(path) > slen else  path

    def escape(self, path):
        """"""
        return path.replace('#', '%23')

    def do_folders(self):
        """"""
        for item in self.filelist.get_dirs():
            if os.path.isdir(os.path.join(self.rpath, item)): # needs thumbnails on folders
                bitem = os.path.basename(item)
                if bitem in self.filelist.logo:
                    self.listing.append({'kind': 'logo', 'name': item, 'basename': bitem, 'height':THM_HT, 'href': "http://"+request.host+'/fs'+'/'+self.escape(item), 'src': self.wpath+self.filelist.logo[bitem]})
                else:
                    self.listing.append({'kind': 'dir',  'name': self.shorter(item, 90), 'basename': bitem, 'href': "http://"+request.host+'/fs'+'/'+self.escape(item)})


    def fs(self, path):
        """main method"""
        if path == '/':
            path=''
        self.rpath = path if path.startswith('/') else f"/{path}".replace('//','/')
        self.wpath = "http://"+request.host.replace(':5000','')+self.rpath+'/'

        self.filelist = FileList(self.rpath)

        comments=self.rpath+" "

        # add directories first
        self.do_folders()

        # add files next

        for item in self.filelist.get_files():

            bitem = os.path.basename(item)

            kind = self.magic(bitem)
            row = {'name': item,
                   'basename': self.escape(self.shorter(bitem, 90)),
                   'href': self.wpath+self.escape(bitem),
                   'src': self.get_src(bitem, default=self.get_dflt_src(kind, bitem)),
                   'width':'', 'height': THM_HT}
            row['kind'] = self.movie_kind if kind == 'movie' else kind
            self.listing.append(row)

        # title plaintitle heading type | navigation db
        page_dict = {
                'title': f"{self.tail(self.rpath,100)} ({len(self.listing)} items)",
                'pagetitle': os.path.basename(self.rpath),
                'heading': 'phpgallery',
                'plaintitle':True,
                'button_class':'fivebuttons',
                'navigation': Navigation(self.rpath)(),
                'type':'fs', 'thm_ht': THM_HT,
        }

        return render_template("fs.html", 
                               webroot="http://"+request.host.replace(':5000',''),
                               page=page_dict, 
                               listing=self.listing, 
                               comments=comments)

    
    def get_dflt_src(self, kind, bitem):
        """"""
        srcs = {'movie': url_for("static", filename="movie-blank-512.png"),
                'image': self.wpath+self.escape(bitem),
                'file': url_for("static",filename="file-blank-512.png")}
        #current_app.logger.info(f"kind={kind}")
        return srcs[kind]


    def get_src(self, bitem, default=""):
        """"""
        for extn in ['.png', '.jpg', '.thm']:
            if os.path.exists(os.path.join(self.rpath+'/.pics/'+os.path.splitext(bitem)[0]+extn)):
                self.movie_kind = 'movie'
                return os.path.join(self.wpath+'.pics/'+os.path.splitext(bitem)[0]+extn)
        self.movie_kind = 'movie_icon'
        return default


class Navigation:
    def __init__(self, rpath):
        """"""
        self.rpath = rpath
        self.upath = os.path.dirname(self.rpath)
        self.wupath = self.upath
        self.dirlist = []

        if self.wupath == '/':
            self.wupath=''

    def get_dir(self, offset):
        """"""
        try:
            return self.dirlist[self.dirlist.index(os.path.basename(self.rpath))+offset]
        except (ValueError,IndexError):
            return ""

    def __call__(self):
        """"""
        self.dirlist = sorted([d for d in os.listdir(self.upath) if os.path.isdir(os.path.join(self.upath,d))])

        prevdir = self.get_dir(-1)
        nextdir = self.get_dir(1)

        return {
            "up": {"href": f"/fs{self.wupath}", "title": "Up", 'class':'', 'rows': 1 },
            "prev": {"href": f"/fs{self.wupath}/{prevdir}", "title": "Prev", 'class':"noanchor" if prevdir=="" else "", 'rows': 1 },
            "next": {"href": f"/fs{self.wupath}/{nextdir}", "title": "Next", 'class':"noanchor" if nextdir=="" else "", 'rows': 1 },
        }


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

