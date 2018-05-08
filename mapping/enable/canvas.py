from __future__ import division, print_function

import math

from enable.api import Canvas, ColorTrait
from kiva.fonttools import str_to_font
from kiva.image import GraphicsContext
from kiva.constants import FILL
from traits.api import Int, Range, Instance, on_trait_change

from .i_tile_manager import ITileManager


class MappingCanvas(Canvas):
    """
    An infinite tiled canvas for showing maps
    """

    tile_cache = Instance(ITileManager)

    tile_alpha = Range(0.0, 1.0, 1.0)

    bgcolor = ColorTrait("lightsteelblue")

    # FIXME This is a hack - remove when viewport is fixed
    _zoom_level = Int(0)

    _blank_tile = Instance(GraphicsContext)

    def __blank_tile_default(self):
        gc = GraphicsContext((256, 256), pix_format='rgba32')
        font = str_to_font('swiss 18')
        gc.clear((0.9, 0.875, 0.85, 1.0))

        text = 'Image not available'
        with gc:
            gc.set_font(font)
            gc.set_stroke_color((0.75, 0.75, 0.75, 1.0))

            width, height, _, _ = gc.get_full_text_extent(text)
            pos = (256 - width) // 2, (256 - height) // 2
            gc.translate_ctm(*pos)
            gc.show_text(text)
        return gc

    def _tile_cache_changed(self, new):
        fmt_map = {3: 'rgb24', 4: 'rgba32'}

        def process(data):
            return GraphicsContext(data, pix_format=fmt_map[data.shape[2]],
                                   interpolation='nearest', bottom_up=True)
        new.process_raw = process

    @on_trait_change('tile_cache:tile_ready')
    def _tile_ready(self, zoom_row_col):
        self.request_redraw()

    def _draw_background(self, gc, view_bounds=None, mode="default"):
        if self.bgcolor not in ("clear", "transparent", "none"):
            with gc:
                gc.set_antialias(False)
                gc.set_fill_color(self.bgcolor_)
                gc.draw_rect(view_bounds, FILL)

        # Call the enable _draw_border routine
        if not self.overlay_border and self.border_visible:
            # Tell _draw_border to ignore the self.overlay_border
            self._draw_border(gc, view_bounds, mode, force_draw=True)
        return

    def _draw_underlay(self, gc, view_bounds=None, mode="default"):
        x, y, width, height = view_bounds
        zoom = self._zoom_level
        with gc:
            # Tile image
            tile_size = self.tile_cache.get_tile_size()
            startx = int(x) // tile_size * tile_size
            starty = int(y) // tile_size * tile_size
            endx = int(x+width)
            endy = int(y+height)

            rows, cols = self.tile_cache.get_data_dimensions(zoom)
            wrap_x, wrap_y = self.tile_cache.get_wrap_flags()
            if not wrap_x:
                startx = max(startx, 0)
                endx = min(endx, cols * tile_size)
            if not wrap_y:
                starty = max(starty, 0)
                endy = min(endy, rows * tile_size)

            gc.set_alpha(self.tile_alpha)
            for tx in range(startx, endx, tile_size):
                for ty in range(starty, endy, tile_size):
                    zoom, row, col = self.tile_cache.convert_to_tilenum(tx, ty,
                                                                        zoom)
                    tile = self.tile_cache.get_tile(zoom, row, col)
                    if not tile:
                        tile = self._blank_tile
                    gc.draw_image(tile, (tx, ty, tile_size+1, tile_size+1))

        super(MappingCanvas, self)._draw_underlay(gc, view_bounds, mode)

    def transformToScreen(self, lat_deg, lon_deg):
        return self._WGS84_to_screen(lat_deg, lon_deg, self._zoom_level)

    def transformToWSG84(self, x, y):
        return self._screen_to_WGS84(x, y, self._zoom_level)

    def _WGS84_to_screen(self, lat_deg, lon_deg, zoom):
        """
         lat = Latitude in degrees
         lon = Longitude in degrees
         zoom = zoom level
        """
        lat_rad = math.radians(lat_deg)
        mapsize = self.tile_cache.get_tile_size() << zoom
        x = (lon_deg + 180.0) / 360.0 * mapsize
        y = (1- (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0) * mapsize  # noqa
        return (x, y)

    def _screen_to_WGS84(self, x, y, zoom):
        mapsize = self.tile_cache.get_tile_size() << zoom
        lon_deg = (x * 360.0 / mapsize) - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (1 - y / mapsize))))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)
