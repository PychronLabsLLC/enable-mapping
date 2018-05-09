
from traits.api import Instance, Str, provides

from .i_tile_manager import ITileManager
from .tile_manager import TileManager
from .cacheing_decorators import lru_cache
from .mbtiles import MbtileSet


@provides(ITileManager)
class MBTileManager(TileManager):

    # ITileManager interface ###########################################
    @lru_cache()
    def get_tile(self, zoom, row, col):
        tile = self._tileset.get_tile(zoom, row, col)
        data = tile.get_png()
        if not data:
            return None
        else:
            return self.process_raw(data)

    def get_tile_size(self):
        return 256

    def convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        size = self.get_tile_size()
        col = (x / size % n)
        row = (y / size % n)
        return (zoom, col, row)

    # Public interface #################################################

    filename = Str()

    # Private interface ##################################################

    _tileset = Instance(MbtileSet)

    def _filename_changed(self, new):
        self._tileset = MbtileSet(mbtiles=new)
        self.get_tile.clear()

    def __tileset_default(self):
        return MbtileSet(mbtiles=self.filename)
