import os.path as pth

import enaml
from enaml.qt.qt_application import QtApplication

from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Constant, Str

from mapping.api import get_builtin_mbtiles_path
from mapping.enable.api import MappingCanvas, MappingViewport, MBTileManager
from mapping.enable.primitives.api import GeoMarker

HERE = pth.dirname(__file__)


class Model(HasTraits):

    title = Constant("Local map with marker")

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    filename = Str


def main():
    tile_layer = MBTileManager(filename=get_builtin_mbtiles_path(),
                               min_level=0, max_level=3)

    canvas = MappingCanvas(tile_cache=tile_layer)

    marker_path = pth.join(HERE, 'enthought-marker.png')
    canvas.add(GeoMarker(filename=marker_path,
                         geoposition=(40.7546423, -73.9748948)))

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))

    model = Model(canvas=canvas, viewport=viewport)

    with enaml.imports():
        from simple_view import Map

    app = QtApplication()
    window = Map(model=model)
    window.show()
    app.start()


if __name__ == "__main__":
    main()
