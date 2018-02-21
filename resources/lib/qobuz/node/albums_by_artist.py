'''
    qobuz.node.albums_by_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcgui
from qobuz.node.inode import INode
import weakref
from qobuz.api import api
from qobuz.gui.contextmenu import contextMenu
from qobuz.node import getNode, Flag
from qobuz.debug import getLogger
logger = getLogger(__name__)

class Node_albums_by_artist(INode):
    '''@class Node_product_by_artist:
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_albums_by_artist, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.ALBUMS_BY_ARTIST
        self.content_type = 'albums'
        self._items_path = 'albums/items'

    def get_label(self, default=None):
        return self.get_artist()

    def get_image(self):
        image = self.get_property('picture')
        image = image.replace('126s', '_')
        return image

    def get_artist(self):
        return self.get_property('name')

    def get_slug(self):
        return self.get_property('slug')

    def get_artist_id(self):
        return self.nid

    def _count(self):
        return len(self.get_property(self._items_path, default=[]))

    def fetch(self, *a, **ka):
        return api.get('/artist/get',
                       artist_id=self.nid,
                       limit=self.limit,
                       offset=self.offset,
                       extra='albums')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if self.count() == 0:
            return False
        for album in self.get_property(self._items_path):
            for k in ['artist', 'interpreter', 'composer', 'performer']:
                try:
                    if k in self.data['artist']:
                        album[k] = weakref.proxy(self.data['artist'][k])
                except:
                    logger.warn("Strange thing happen")
                    pass
            self.add_child(getNode(Flag.ALBUM, data=album))
        return True

    def makeListItem(self, replaceItems=False):
        item = xbmcgui.ListItem(
            self.get_label(),
            self.get_label(),
            self.get_image(),
            self.get_image(),
            self.make_url(), )
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item
