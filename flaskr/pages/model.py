
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

from flask import render_template

from flaskr.pages.base import HtmlSite, PageInfo, PageBuilder


class HtmlModelPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)
        self.modelid = None

    def do_page(self, modelid):
        """list all photo sets and videos of a model"""
        self.modelid = modelid
        #modelpage = ModelPage([self.galdict, self.viddict], modelid, self.db)
        info = PageInfo([self.galdict, self.viddict], 'model', filtid=modelid)
        pagebuilder = PageBuilder(info, self)
        page_dict, gvdicts = pagebuilder.build()

        # next/prev needs to follow sort order of models page above
        nmodel, pmodel, nname, pname = self.db.models_table().get_next_prev(modelid)

        page_dict['nid'] = nmodel
        page_dict['pid'] = pmodel
        page_dict['next'] = nname
        page_dict['prev'] = pname

        modelname = self.db.models_table().select_where('id', modelid)[0][1]
        page_dict['title'] = modelname

        return render_template("model_page.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=gvdicts[0],
                               viddicts=gvdicts[1])

    def getitems(self, order):
        order_by = {
            'alpha': 'asc',  'ralpha': 'desc',
            'id':    'asc',  'rid':    'desc',
            'date':  'asc',  'rdate':  'desc'
            }
        unsorted_photos = self.db.photos_table().select_where_group_by('model_id',self.modelid,'id')
        #    id, model_id, site_id, name, location, thumb, count, pdate = gallery
        unsorted_videos = self.db.videos_table().select_where_group_by('model_id',self.modelid,'id')

        photos = []
        videos = []
        # lambda is setting the database column to sort on - date is different between photos and videos
        if order in ('alpha', 'ralpha'):
            photos = sorted(unsorted_photos, key = lambda x: x[3]) #name
            videos = sorted(unsorted_videos, key = lambda x: x[3])
        elif order in ('id', 'rid'):
            photos = sorted(unsorted_photos, key = lambda x: x[0]) # id
            videos = sorted(unsorted_videos, key = lambda x: x[0])
        elif order in ('date', 'rdate'):
            photos = sorted(unsorted_photos, key = lambda x: x[7])  #pdate
            videos = sorted(unsorted_videos, key = lambda x: x[10]) #vdate

        if order_by[order] == 'desc':
            photos.reverse()
            videos.reverse()
        return (photos, videos)



class HtmlModelsPage(HtmlSite):

    def __init__(self, dbname):
        """"""
        super().__init__(dbname)

    def do_page(self):
        """list all models"""
        #modelspage = ModelsPage([self.moddict,], self.db.models_table())
        info = PageInfo([self.moddict,], 'models')
        pagebuilder = PageBuilder(info, self)
        page_dict, galldicts = pagebuilder.build()
        return render_template("photos.html",
                               webroot=self.config['webroot'],
                               page=page_dict,
                               galldicts=galldicts[0])

    def getitems(self, order):
        order_by = {
            'alpha':   'asc',   'ralpha':   'desc',
            'vlatest': 'desc',  'rvlatest': 'asc',
            'platest': 'desc',  'rplatest': 'asc',
            'most':    'desc',  'least':    'asc',
            'id':      'asc',   'rid':      'desc'
        }
        if order in ['alpha', 'ralpha']:
            models = self.db.models_table().select_group_by_order_by('name', 'name', order_by[order])

        elif order in ['vlatest', 'rvlatest']:
            models = self.db.models_table().select_by_most_recent_videos('model_id', order_by[order])

        elif order in ['platest', 'rplatest']:
            models = self.db.models_table().select_by_most_recent_photos('model_id', order_by[order])

        elif order in ['most', 'least']:
            models = self.db.models_table().select_models_by_count(order_by[order])

        elif order in ['id', 'rid']:
            models = self.db.models_table().select_order_by('id', order_by[order])

        if len(models) == 0:
            models = self.db.models_table().select_order_by('id', 'desc')

        return (models,)

