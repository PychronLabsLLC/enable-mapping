
import enaml
from enaml.qt.qt_application import QtApplication

from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str

from mapping.api import get_builtin_mbtiles_path, MBTileManager
from mapping.enable.api import MappingCanvas, MappingViewport


class Model(HasTraits):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    filename = Str


def main():
    tile_layer = MBTileManager(filename=get_builtin_mbtiles_path(),
                               min_level=0,
                               max_level=3)

    canvas = MappingCanvas(tile_cache=tile_layer)

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
