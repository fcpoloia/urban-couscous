
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

import sys
from flask import render_template, current_app
from flask.views import View

#from flaskr.collections import DBItems, DBItemsIterator
from flaskr.pages.base import HtmlSite #, PageInfo, PageBuilder
#from flaskr.pages.sorttypes import vsorting


# @app.route("/<dbname>/video/site/<sid>/<vid>")
# @app.route("/<dbname>/video/model/<mid>/<vid>")
# @app.route("/<dbname>/video/<page>/<pageid>/<vid>")

class VideoPageView(View):
    methods = ["POST", "GET"]

    def __init__(self, root=None):
        """"""
        self.root = True

    def dispatch_request(self, dbname, page, pageid, vid=None):
        """"""
        mysite = HtmlVideoPage(dbname)
        mysite.heading('videos')
        return mysite.do_page(vid, page, pageid)


class HtmlVideoPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)


    def do_page(self, vid, page=None, pageid=None): #sid=None, mid=None):
        """single video page"""
        video = self.db.videos_table().select_where('id', vid)[0]
        _idx, model_id, site_id, name, filename, thumb, poster, width, height, _length, _vdate = video
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

        current_app.logger.info(f"nv {nvideo}, pv {pvideo}, nn {nname}, pn {pname}\n")

        #self.heading('videos')
        prefix = f"{page}/{pageid}/" if page is not None else ""

        titledict = {
            'site': {'href':f"/sites/{self.dbname}/{site_id}",
                     'name':sitename},
            'models':[{'href':f"/models/{self.dbname}/{model_id}",
                       'name':modelname}],
            'folder': name
        }

        # title plaintitle heading type | navigation db
        page_dict = self.init_page_dict(titledict, False, 'videos') #, self.links)
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


# class HtmlVideosPage(HtmlSite):

#     def __init__(self, dbname):
#         """"""
#         super().__init__(dbname)
#         self._dbitems = DBItems()

#     def do_page(self):
#         """list all videos"""
#         #videospage = VideosPage([self.viddict,], self.db.videos_table())
#         info = PageInfo([self.viddict,], 'videos')
#         pagebuilder = PageBuilder(info, self)
#         page_dict, viddicts = pagebuilder.build()
#         return render_template("videos.html",
#                                webroot=self.config['webroot'],
#                                page=page_dict,
#                                viddicts=viddicts[0])

#     def getitems(self, order):
#         items = self.db.videos_table().select_order_by(vsorting[order][1], vsorting[order][2])
#         if len(items) == 0:
#             items = self.db.videos_table().select_group_by_order_by('id', 'id', 'desc')
#         self._dbitems.addVideoMembers(items)
#         return (items,)

