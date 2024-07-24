
import os
from html.entities import html5

from flask import request, render_template

from flaskr.pages.base import HtmlSite


# -----------------------------------------------------------------------------
# To Do:
# - this class should be in a new file
# - custom default sorting
# - use of Sort menu items
# - read .ignore file
# - implement paging (max 500 items)
# - add a 'show hidden files' option
# - videos should point to a videos page
# - need to change cdd for plain files and non-logo folders when mixed with images
# - remove the Random button
# - deal with Permission Denied errors
#
class HtmlFileSystem(HtmlSite):
    """search all databases"""

    def __init__(self):
        """"""
        super().__init__()
        self.rpath=''
        self.wpath=''

    def ignored(self, item):
        ignlist = ['.ignore', 'comments', 'comments.php', 'movie_dims']
        return item.startswith('.') or item in ignlist

    def magic(self, item):
        exten = os.path.splitext(item)[1].lower()
        if exten in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        if exten in ['.mp4', '.mkv']:
            return 'movie'
        return ''

    def load_logo(self):
        logo={}
        if os.path.exists(os.path.join(self.rpath, '.logo')):
            with open(os.path.join(self.rpath, '.logo'), 'r') as fp:
                lines = fp.readlines()
                for line in lines:
                    d, p = line.split(',')[:2]
                    logo[d] = p
        return logo

    def shorter(self, path, slen=25):
        return path[:slen]+html5["hellip;"] if len(path) > slen else  path

    def tail(self, path, slen=150):
        return html5["hellip;"]+path[-slen:] if len(path) > slen else  path

    def fs(self, path):
        """"""
        if path == '/': 
            path=''
        self.rpath = path if path.startswith('/') else f"/{path}".replace('//','/')
        self.wpath = "http://"+request.host.replace(':5000','')+'/'+path+'/'
        upath = os.path.dirname('/'+path)
        wupath = upath
        if wupath == '/': 
            wupath=''

        n=p=''
        nr=pr=0
        dirlist = sorted([d for d in os.listdir(upath) if os.path.isdir(os.path.join(upath,d))])
        for c in range(len(dirlist)):
            if dirlist[c] == os.path.basename('/'+path):
                if c > 0:
                    p = dirlist[c-1]
                    pr=1
                if c < len(dirlist)-1:
                    n = dirlist[c+1]
                    nr=1

        links = {
            "up": {"href": f"/fs{wupath}", "title": "Up", 'class':'', 'rows': 1 },
            "prev": {"href": f"/fs{wupath}/{p}", "title": "Prev", 'class':'', 'rows': pr },
            "next": {"href": f"/fs{wupath}/{n}", "title": "Next", 'class':'', 'rows': nr },
        }

        logo = self.load_logo()
        listing=[]
        dirlist = sorted([d for d in os.listdir(self.rpath) if os.path.isdir(os.path.join(self.rpath,d)) and not self.ignored(d)])
        for item in dirlist:
            if os.path.isdir(os.path.join(self.rpath, item)): # needs thumbnails on folders
                if item in logo:
                    listing.append({'kind': 'logo', 'name': item, 'basename': item, 'height':'240px', 'href':"http://"+request.host+'/fs'+self.rpath+'/'+item, 'src': self.wpath+logo[item]})
                else:
                    listing.append({'kind': 'dir', 'name': self.shorter(item), 'href': "http://"+request.host+'/fs'+self.rpath+'/'+item})

        dirlist = sorted([i for i in os.listdir(self.rpath) if not os.path.isdir(os.path.join(self.rpath,i))])
        for item in dirlist:

            if self.ignored(item):
                continue

            # check for movies, images, pdf
            if self.magic(item) == 'image': # needs basename, height
                if os.path.exists(self.rpath+"/.pics/"+os.path.splitext(item)[0]+'.png'):
                    src = self.wpath+".pics/"+os.path.splitext(item)[0]+'.png'
                if os.path.exists(self.rpath+"/.pics/"+os.path.splitext(item)[0]+'.jpg'):
                    src = self.wpath+".pics/"+os.path.splitext(item)[0]+'.jpg'
                else:
                    src = self.wpath+item
                listing.append({'kind': 'image', 'name': item, 'basename': item, 'height': '240px', 'href': self.wpath+item, 'src': src})

            elif self.magic(item) == 'movie': # needs h, w, mlen
                src="/static/MovieClip.png" #'w':'209', 'h':'224'
                thm=False
                if os.path.exists(os.path.join(self.rpath+'/.pics/'+os.path.splitext(item)[0]+'.png')):
                    src = os.path.join(self.wpath+'.pics/'+os.path.splitext(item)[0]+'.png')
                    #thm=True
                elif os.path.exists(os.path.join(self.rpath+'/.pics/'+os.path.splitext(item)[0]+'.thm')):
                    src = os.path.join(self.wpath+'.pics/'+os.path.splitext(item)[0]+'.thm')
                listing.append({'kind': 'movie', 'name': item, 'href': self.wpath+item, 'src': src, 'thm':thm, 'height':'240px'})

            else:
                listing.append({'kind': 'file', 'name': item, 'href': self.wpath+item})

        # title plaintitle heading type | navigation db
        page_dict = {
            'title': f"{self.tail(path,100)} ({len(listing)} items)",
            'heading':'phpgallery',
            'plaintitle':True,
            'button_class':'fivebuttons',
            'navigation':links,
            'fs': True
        }


        return render_template("fs.html", webroot="http://"+request.host.replace(':5000',''),
                                page=page_dict, listing=listing)

