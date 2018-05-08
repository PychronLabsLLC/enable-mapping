import os.path as pth

from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str

from mapping.enable.api import MappingCanvas, MappingViewport, MBTileManager

HERE = pth.dirname(__file__)


class Model(HasTraits):

    canvas = Instance(MappingCanvas)
    viewport = Instance(MappingViewport)

    filename = Str


def main():
    tiles_path = pth.join(HERE, "..", "data", "map.mbtiles")
    tile_layer = MBTileManager(filename=tiles_path,
                               min_level=0,
                               max_level=3)

    canvas = MappingCanvas(tile_cache=tile_layer)

    viewport = MappingViewport(component=canvas)
    viewport.tools.append(ViewportPanTool(viewport))

    model = Model(canvas=canvas, viewport=viewport)

    import enaml
    with enaml.imports():
        from simple_view import Map
    window = Map(model=model)
    window.show()


if __name__ == "__main__":
    main()
