from unittest import TestCase

from kiva.image import Image

from mapping.enable.canvas import MappingCanvas
from mapping.enable.api import MBTileManager


class TestMappingCanvas(TestCase):
    def setUp(self):
        tile_layer = MBTileManager(filename='map.mbtiles',
                                   min_level=2, max_level=4)

        self.canvas = MappingCanvas(tile_cache=tile_layer)

    def test__blank_tile(self):
        self.assertIsInstance(self.canvas._blank_tile, Image)