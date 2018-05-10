import unittest

from kiva.image import Image

from mapping.api import MBTileManager, get_builtin_mbtiles_path
from mapping.enable.api import MappingCanvas


class TestMappingCanvas(unittest.TestCase):
    def setUp(self):
        tile_layer = MBTileManager(filename=get_builtin_mbtiles_path(),
                                   min_level=2, max_level=4)
        self.canvas = MappingCanvas(tile_cache=tile_layer)

    def test_blank_tile(self):
        self.assertIsInstance(self.canvas._blank_tile, Image)
