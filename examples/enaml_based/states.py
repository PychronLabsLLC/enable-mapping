
import os.path as pth

import enaml
from enaml.qt.qt_application import QtApplication

from traits.api import HasTraits, Constant, Instance
from enable.tools.api import ViewportPanTool

from mapping.api import get_builtin_mbtiles_path
from mapping.enable.api import (MappingCanvas, MappingViewport, MBTileManager,
                                GeoJSONOverlay)

HERE = pth.dirname(__file__)


class SingleMap(HasTraits):

    title = Constant("Map with GeoJSON")

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)


def main():
    tile_layer = MBTileManager(filename=get_builtin_mbtiles_path(),
                               min_level=2, max_level=4)

    canvas = MappingCanvas(tile_cache=tile_layer)
    states_path = pth.join(HERE, 'states.geojs')
    canvas.overlays.append(GeoJSONOverlay(component=canvas,
                                          geojs_filename=states_path))

    viewport = MappingViewport(component=canvas, zoom_level=3,
                               geoposition=(37.09024, -95.712891))
    viewport.tools.append(ViewportPanTool(viewport))

    model = SingleMap(canvas=canvas,
                      viewport=viewport)

    with enaml.imports():
        from simple_view import Map

    app = QtApplication()
    window = Map(model=model)
    window.show()
    app.start()


if __name__ == "__main__":
    main()
