from __future__ import division

from io import BytesIO
import os
import os.path as op

import numpy as np
from PIL import Image

from traits.api import String, Tuple, provides

from .cacheing_decorators import lru_cache
from .i_tile_manager import ITileManager
from .tile_manager import TileManager


@provides(ITileManager)
class ImageTileManager(TileManager):

    lod_dir = String
    _level_dimensions = Tuple

    @lru_cache(maxsize=256)
    def get_tile(self, zoom, row, col):
        if zoom >= len(self._level_dimensions):
            return None

        # Flip the Y axis
        num_rows, _ = self.get_data_dimensions(zoom)
        row = num_rows - 1 - row

        zoom_dir = op.join(self.lod_dir, str(int(zoom)))
        tile_path = op.join(zoom_dir, '{}.{}.npy'.format(row, col))
        if not op.exists(tile_path):
            return None

        tile = np.load(tile_path)
        img = Image.fromarray(tile, mode='RGB')
        data = BytesIO()
        img.save(data, format='png')
        return self.process_raw(data.getvalue())

    def get_tile_size(self):
        return 256

    def get_data_dimensions(self, zoom):
        num_levels = len(self._level_dimensions)
        if zoom >= num_levels:
            return 0, 0
        return self._level_dimensions[zoom]

    def get_wrap_flags(self):
        return False, False

    def convert_to_tilenum(self, x, y, zoom):
        n = 2 ** zoom
        size = self.get_tile_size()
        col = x // size % n
        row = y // size % n
        return zoom, row, col

    def _lod_dir_changed(self, new):
        self.get_tile.clear()

        level_dimensions = _get_lod_dir_details(new)
        self._level_dimensions = level_dimensions
        self.min_level = 0
        self.max_level = len(level_dimensions)


def _get_lod_dir_details(path):
    level_count = 0
    level_dimensions = []

    for fn in os.listdir(path):
        if op.isdir(op.join(path, fn)):
            level_count += 1

    for i in range(level_count):
        level_dirpath = op.join(path, str(i))
        if op.exists(level_dirpath) and op.isdir(level_dirpath):
            rows, cols = 0, 0
            for fn in os.listdir(level_dirpath):
                try:
                    r, c = fn.split('.', 2)[:2]
                    rows, cols = max(rows, int(r)), max(cols, int(c))
                except ValueError:
                    # Ignore bad filenames (like .DS_Store...)
                    pass
            level_dimensions.append((rows + 1, cols + 1))
        else:
            # Missing level directory! Bail out.
            return ()

    return tuple(level_dimensions)
