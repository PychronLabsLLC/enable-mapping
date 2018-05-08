from __future__ import print_function

import logging

import requests

from traits.api import Int, Str, on_trait_change, Instance, provides
from pyface.gui import GUI

from .i_tile_manager import ITileManager
from .tile_manager import TileManager
from .cacheing_decorators import lru_cache
from .async_loader import AsyncLoader, AsyncRequest, get_global_async_loader
from .utils import img_data_to_img_array


@provides(ITileManager)
class HTTPTileManager(TileManager):

    #: The async_loader instance used to load the tiles.
    async_loader = Instance(AsyncLoader)

    # ITileManager interface ################################################

    def get_tile_size(self):
        return 256

    def convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        size = self.get_tile_size()
        col = (x / size % n)
        row = (n - 1 - y / size % n)
        return (zoom, row, col)

    @lru_cache()
    def get_tile(self, zoom, row, col):
        # Schedule a request to get the tile
        self.async_loader.put(TileRequest(self._tile_received,
                                          self.server, self.port, self.url,
                                          dict(zoom=zoom, row=row, col=col)))
        # return a blank tile for now
        return None

    # Public interface ################################################

    server = Str
    port = Int(80)
    url = Str

    # Private interface ##################################################

    def _async_loader_default(self):
        return get_global_async_loader()

    def _tile_received(self, tile_args, data):
        zoom, row, col = tile_args['zoom'], tile_args['row'], tile_args['col']
        try:
            img = img_data_to_img_array(data)
            img = self.process_raw(img)
            self.get_tile.replace(img, self, zoom, row, col)
            self.tile_ready = (zoom, row, col)
        except Exception:
            # Failed to process tile
            logging.exception(
                "Failed to process %s%s",
                self.server,
                self.url % tile_args,
            )

    @on_trait_change('server, url')
    def _reset_cache(self, new):
        self.get_tile.clear()
        # This is a hack to repaint
        self.tile_ready = 0, 0, 0


class TileRequest(AsyncRequest):
    def __init__(self, handler, host, port, url, tile_args):
        self.handler = handler
        self._host = host
        self._url = url
        self._tile_args = tile_args

    def execute(self):
        url = 'http://' + self._host + self._url % self._tile_args
        try:
            r = requests.get(url)
            if r.status_code == 200:
                GUI.invoke_later(self.handler, self._tile_args, r.content)
        except requests.exceptions.RequestException as ex:
            print("Exception in request '{}': {}".format(self, ex))

    def __str__(self):
        return "TileRequest for %s" % str(self._tile_args)

    def __repr__(self):
        return str(self)
