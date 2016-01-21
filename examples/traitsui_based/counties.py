""" Demo of a simple Enable canvas displaying all US counties as an overlay.
Counties data is loaded from a local geojson file.

This is the TraitsUI version of the corresponding demo in the enaml_based
example folder.
"""

from traits.api import HasTraits, Instance
from traitsui.api import Item, ModelView, View
from enable.api import ComponentEditor
from enable.tools.api import ViewportPanTool

from mapping.enable.api import MappingCanvas, MappingViewport, MBTileManager, \
                               GeoJSONOverlay, HTTPTileManager


class SingleMap(HasTraits):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)


class SingleMapView(ModelView):
    model = Instance(SingleMap)

    view = View(
        Item("model.viewport", editor=ComponentEditor(), show_label=False),
        width=800, height=800, title="Map with GeoJSON",
        resizable=True
    )


def main():
    tile_layer = MBTileManager(filename = 'map.mbtiles',
                               min_level = 2,
                               max_level = 4)

    url_pattern = '/v3/mapbox.mapbox-simple/%(zoom)d/%(row)d/%(col)d.png'
    tile_layer = HTTPTileManager(min_level=0, max_level=15,
                                 server='d.tiles.mapbox.com', url=url_pattern)

    canvas = MappingCanvas(tile_cache = tile_layer)
    canvas.overlays.append(GeoJSONOverlay(component=canvas,
                                          geojs_filename='counties.geojs'))

    viewport = MappingViewport(component=canvas, zoom_level=2,
                               geoposition=(37.09024, -95.712891))
    viewport.tools.append(ViewportPanTool(viewport))

    model = SingleMap(canvas=canvas, viewport=viewport)
    view = SingleMapView(model=model)
    view.configure_traits()


if __name__ == "__main__":
    main()
