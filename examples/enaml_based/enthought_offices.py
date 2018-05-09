import os.path as op

import enaml
from enaml.qt.qt_application import QtApplication

from enable.tools.api import ViewportPanTool
from traits.api import HasTraits, Instance, Str, List, Tuple, Float

from mapping.enable.api import MappingCanvas, MappingViewport, HTTPTileManager
from mapping.enable.primitives.api import GeoMarker

HERE = op.dirname(__file__)


class Office(HasTraits):
    location = Tuple(Float, Float)
    city = Str


class MultiMap(HasTraits):

    title = Str("Enthought Offices Worldwide")
    offices = List(Office)

    canvas = Instance(MappingCanvas)
    viewports = List(MappingViewport)

    def add_office(self, city, location):
        offices = self.offices[:]
        viewports = self.viewports[:]

        office = Office(city=city, location=location)
        canvas = self.canvas

        canvas.add(GeoMarker(geoposition=office.location,
                             filename='enthought-marker.png'))

        viewport = MappingViewport(component=canvas)
        viewport.tools.append(ViewportPanTool(viewport))
        viewport.set(zoom_level=canvas.tile_cache.max_level - 3,
                     geoposition=office.location)
        offices.append(office)
        viewports.append(viewport)
        self.trait_setq(offices=offices)
        self.viewports = viewports

    def _offices_changed(self, new):
        viewports = []
        canvas = self.canvas
        marker_path = op.join(HERE, 'enthought-marker.png')
        for office in new:
            canvas.add(GeoMarker(geoposition=office.location,
                                 filename=marker_path))

            viewport = MappingViewport(component=canvas)
            viewport.tools.append(ViewportPanTool(viewport))
            viewport.set(zoom_level=canvas.tile_cache.max_level - 3,
                         geoposition=office.location)
            viewports.append(viewport)
        self.viewports = viewports


def main():
    manager = HTTPTileManager(min_level=0, max_level=15,
                              server='tile.openstreetmap.org',
                              url='/%(zoom)d/%(row)d/%(col)d.png')
    canvas = MappingCanvas(tile_cache=manager)

    nyc = Office(city="New York City", location=(40.7546423, -73.9748948))
    austin = Office(city="Austin", location=(30.267651, -97.7424769))
    cambridge = Office(city="Cambridge", location=(52.2098683, 0.0904441))
    mumbai = Office(city="Mumbai", location=(19.1125289, 72.9081059))

    model = MultiMap(canvas=canvas, offices=[nyc, austin, cambridge, mumbai])

    with enaml.imports():
        from office_view import Main

    app = QtApplication()
    window = Main(model=model)
    window.show()
    app.start()


if __name__ == "__main__":
    main()
