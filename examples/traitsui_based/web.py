""" Demo pulling tiles from various open tile servers, and displaying a point
marker on the earth (in New York).

This is the TraitsUI version of the corresponding demo in the enaml_based
example folder.
"""
from enable.api import ComponentEditor
from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, Dict
from traitsui.api import Item, View

from mapping.enable.api import MappingCanvas, MappingViewport, HTTPTileManager
from mapping.enable.primitives.api import GeoCircle

SERVERS = {
    'OpenStreetMap': ('tile.openstreetmap.org',
                      '/%(zoom)d/%(col)d/%(row)d.png'),
    'Stamen Watercolor': ('a.tile.stamen.com',
                          '/watercolor/%(zoom)d/%(col)d/%(row)d.jpg'),
    'Stamen Terrain': ('tile.stamen.com',
                       '/terrain-background/%(zoom)d/%(col)d/%(row)d.png'),
}


class WebModel(HasTraits):

    server = Str
    servers = Dict

    def _server_changed(self, new):
        server, url = self.servers[new]
        self.canvas.tile_cache.trait_set(server=server, url=url)

    def _servers_default(self):
        return SERVERS


class SingleMap(WebModel):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    view = View(
        Item("viewport", editor=ComponentEditor(), show_label=False)
    )


def main():

    tile_manager = HTTPTileManager(min_level=0, max_level=15)
    canvas = MappingCanvas(tile_cache=tile_manager)

    nyc = (40.7546423, -73.9748948)
    canvas.add(GeoCircle(radius=4, geoposition=nyc))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))
    viewport.set(zoom_level=12, geoposition=nyc)

    model = SingleMap(canvas=canvas, viewport=viewport,
                      server='OpenStreetMap')
    model.configure_traits()


if __name__ == "__main__":
    main()
