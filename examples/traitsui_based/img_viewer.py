from __future__ import division

from chaco.api import (
    ArrayDataSource, DataRange1D, LinearMapper, OverlayPlotContainer, PlotAxis,
    add_default_axes, add_default_grids)
from chaco.tools.api import PanTool, ZoomTool

from mapping.chaco.map import Map
from mapping.chaco.null_renderer import NullPlotRenderer
from mapping.enable.img_tile_manager import ImageTileManager


def build_formatter(maxval, flip=False):
    if flip:
        def convert(x):
            return '{:.0f}'.format((1.0 - x) * maxval)
    else:
        def convert(x):
            return '{:.0f}'.format(x * maxval)
    return convert


def create_plot_component(lod_dir):
    tile_cache = ImageTileManager(lod_dir=lod_dir)
    tile_size = tile_cache.get_tile_size()
    max_rows, max_cols = tile_cache.get_data_dimensions(-1)

    index = ArrayDataSource()
    index_range = DataRange1D(low=0, high=1)
    index_range.add(index)
    index_mapper = LinearMapper(range=index_range)

    value = ArrayDataSource()
    value_range = DataRange1D(low=0, high=1)
    value_range.add(value)
    value_mapper = LinearMapper(range=value_range)

    plot = NullPlotRenderer(index=index, value=value,
                            index_mapper=index_mapper,
                            value_mapper=value_mapper,
                            orientation='h', border_visible=True)
    add_default_axes(plot, vtitle='Y', htitle='X')
    add_default_grids(plot)

    overlay = Map(plot, tile_cache=tile_cache, zoom_level=1)
    plot.underlays.insert(0, overlay)
    plot.tools.append(PanTool(plot))
    plot.tools.append(ZoomTool(plot))

    axis = get_plot_axis(plot, 'left')
    if axis:
        axis.tick_label_formatter = build_formatter(max_rows * tile_size, True)
    axis = get_plot_axis(plot, 'bottom')
    if axis:
        axis.tick_label_formatter = build_formatter(max_cols * tile_size)

    container = OverlayPlotContainer(use_backbuffer=True, padding=75)
    container.add(plot)
    container.bgcolor = "lightgray"
    return container


def get_plot_axis(renderer, orientation):
    for c in renderer.underlays:
        if isinstance(c, PlotAxis) and c.orientation == orientation:
            return c


if __name__ == "__main__":
    import argparse
    from enable.api import Component, ComponentEditor
    from traits.api import HasTraits, Constant, Instance
    from traitsui.api import View, UItem

    ap = argparse.ArgumentParser()
    ap.add_argument('path', help='A path to an LOD directory')
    args = ap.parse_args()

    class Demo(HasTraits):
        title = Constant('Image Tiler Demo')
        plot = Instance(Component)

        traits_view = View(
            UItem('plot', editor=ComponentEditor()),
            width=1000, height=1000, resizable=True,
            title='title'
        )

        def _plot_default(self):
            return create_plot_component(args.path)

    demo = Demo()
    demo.configure_traits()
