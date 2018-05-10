import os.path as pth

import enaml
from enaml.qt.qt_application import QtApplication
import numpy as np
import pandas

from chaco.api import (
    ArrayDataSource, ColorBar, HPlotContainer, OverlayPlotContainer,
    LinearMapper, DataRange1D, PlotAxis, Blues as colormap)
from chaco.tools.api import PanTool, ZoomTool
from enable.api import Component
from enable.compiled_path import CompiledPath
from traits.api import HasTraits, Instance, List, Str

from mapping.api import HTTPTileManager
from mapping.chaco.api import ChoroplethPlot

DATA_DIR = pth.join(pth.dirname(__file__), '..', 'data')


def create_colorbar(plt):
    colormap = plt.color_mapper
    colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        orientation='v',
                        resizable='v',
                        width=30,
                        padding=20)
    colorbar.plot = plt
    return colorbar


def _create_plot_component(max_pop, index_ds, value_ds, color_ds, paths):

    tile_cache = HTTPTileManager(min_level=2, max_level=4,
                                 server='tile.cloudmade.com',
                                 url='/1a1b06b230af4efdbb989ea99e9841af/20760/256/%(zoom)d/%(col)d/%(row)d.png')  # noqa

    color_range = DataRange1D(color_ds, low_setting=0)

    choro = ChoroplethPlot(
              index=index_ds,
              value=value_ds,
              color_data=color_ds,
              index_mapper=LinearMapper(range=DataRange1D(index_ds)),
              value_mapper=LinearMapper(range=DataRange1D(value_ds)),
              color_mapper=colormap(range=color_range),
              outline_color='white',
              line_width=1.5,
              fill_alpha=1.,
              compiled_paths=paths,

              tile_cache=tile_cache,
              zoom_level=3,
              )

    container = OverlayPlotContainer(
        bgcolor='sys_window', padding=50, fill_padding=False,
        border_visible=True,
    )
    container.add(choro)

    for dir in ['left']:
        axis = PlotAxis(tick_label_formatter=convert_lat,
                        mapper=choro.value_mapper, component=container,
                        orientation=dir)
        container.overlays.append(axis)
    for dir in ['top', 'bottom']:
        axis = PlotAxis(tick_label_formatter=convert_lon,
                        mapper=choro.index_mapper, component=container,
                        orientation=dir)
        container.overlays.append(axis)

    choro.tools.append(PanTool(choro))
    choro.tools.append(ZoomTool(choro))

    colorbar = create_colorbar(choro)
    colorbar.padding_top = container.padding_top
    colorbar.padding_bottom = container.padding_bottom

    plt = HPlotContainer(use_backbuffer=True)
    plt.add(container)
    plt.add(colorbar)
    plt.bgcolor = "sys_window"

    return plt


def convert_lon(lon):
    val = (360.*lon) - 180.
    return ("%.0f" % val)


def convert_lat(lat):
    val = np.degrees(np.arctan(np.sinh(np.pi*(1-2*(1-lat)))))
    return ("%.0f" % val)


class Demo(HasTraits):

    title = Str

    data_columns = List
    column = Str

    index_ds = Instance(ArrayDataSource, ())
    value_ds = Instance(ArrayDataSource, ())
    color_ds = Instance(ArrayDataSource, ())

    dataframe = Instance(pandas.DataFrame)

    plot = Instance(Component)
    paths = List

    def _plot_default(self):
        high = max(self.dataframe[self.dataframe.columns[1]])
        return _create_plot_component(high, self.index_ds, self.value_ds,
                                      self.color_ds, self.paths)

    def _column_changed(self, new):
        self.color_ds.set_data(np.array(self.dataframe[new]))

    def _color_ds_default(self):
        return ArrayDataSource(np.array(self.dataframe[self.column]))

    def _column_default(self):
        return self.dataframe.columns[-1]

    def _data_columns_default(self):
        return list(self.dataframe.columns[1:][::-1])


if __name__ == "__main__":
    from mapping.enable.geojson_overlay import process_raw

    population_filepath = pth.join(DATA_DIR, 'state_populations.csv')
    populations = pandas.read_csv(population_filepath)

    with open(pth.join(DATA_DIR, 'states.geojs'), 'r') as fp:
        polys = process_raw(fp.read().replace('\r\n', ''))
    # generate compiled paths from polys
    paths = []
    coords = np.zeros((len(polys), 2))
    for poly, coord in zip(polys, coords):
        path = CompiledPath()
        total = np.sum((np.sum(p, axis=0) for p in poly), axis=0)
        coord[:] = total/sum(map(len, poly))
        for p in poly:
            path.lines(p - coord)  # recenter on origin
        paths.append(path)

    with enaml.imports():
        from choropleth_view import MapView

    app = QtApplication()
    view = MapView(
        model=Demo(title="State population from 1900 to 2010",
                   index_ds=ArrayDataSource(coords[:, 0]),
                   value_ds=ArrayDataSource(coords[:, 1]),
                   paths=paths,
                   dataframe=populations),
    )
    view.show()
    app.start()
