
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

from flask import render_template

from flaskr.pages.base import HtmlSite, PageInfo, PageBuilder
from flaskr.pages.sorttypes import sorting, vsorting


class HtmlSitePage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self.siteid = None

    def do_page(self, siteid):
        """list all photo sets amd videos of a site"""
        self.siteid = siteid
        #sitepage = SitePage([self.galdict, self.viddict], siteid, self.db)
        info = PageInfo([self.galdict, self.viddict], 'site', filtid=siteid)
        pagebuilder = PageBuilder(info, self)
        page_dict, gvdicts = pagebuilder.build()

        # next/prev needs to follow sort order of sites page above
        nsite, psite, nname, pname = self.db.sites_table().get_next_prev(siteid)

        page_dict['nid'] = nsite
        page_dict['pid'] = psite
        page_dict['next'] = nname
        page_dict['prev'] = pname

        sitename = self.db.sites_table().select_where('id', self.siteid)[0][1]
        page_dict['title'] = sitename

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=gvdicts[0],
                               viddicts=gvdicts[1])

    def getitems(self, order):
        photos = self.db.photos_table().select_where_order_by('site_id', self.siteid, sorting[order][0], sorting[order][2])
        videos = self.db.videos_table().select_where_order_by('site_id', self.siteid, vsorting[order][0], vsorting[order][2])
        return (photos, videos)



class HtmlSitesPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all sites"""
        #sitespage = SitesPage([self.sitdict,], self.db.sites_table())
        info = PageInfo([self.sitdict,], 'sites')
        pagebuilder = PageBuilder(info, self)
        page_dict, galldicts = pagebuilder.build()
        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts[0])

    def getitems(self, order):
        order_by = {'most': 'desc', 'least': 'asc'}

        if order in ['most', 'least']:
            sites = self.db.sites_table().select_sites_by_count(order_by[order])
        else:
            sites = self.db.sites_table().select_group_by_order_by(sorting[order][0], sorting[order][1], sorting[order][2])
        return (sites,)

