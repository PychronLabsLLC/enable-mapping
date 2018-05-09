from enable.primitives.shape import Shape
from enable.enable_traits import coordinate_trait
from traits.api import Property, Bool, property_depends_on


class GeoPrimitive(Shape):
    """ Coordinates are in Lat/Long using WGS84 Datum
    """

    geoposition = coordinate_trait

    scale_with_zoom = Bool(False)

    position = Property(coordinate_trait)

    @property_depends_on('geoposition,bounds,container,container:_zoom_level')
    def _get_position(self):
        # Translate the geoposition to screen space
        lat, lon = self.geoposition
        if self.container:
            x, y = self.container.transformToScreen(lat, lon)
        else:
            x, y = 0., 0.
        # shift based on bounds
        w, h = self.bounds
        return x-w/2., y-h/2.

    def _set_position(self, pos):
        x, y = pos
        if self.container:
            lat_deg, lon_deg = self.container.transformToWGS84(x, y)
            w, h = self.bounds
            self.position = [x+w/2., y+h/2.]

    def _draw_mainlayer(self, gc, view_bounds=None, mode='default'):
        """ Draw the component. """
        with gc:
            x, y = self.position

            # FIXME - this is broken when there are multiple
            # viewports
            if not self.scale_with_zoom:
                zoom = max([v.zoom for v in self.container.viewports])

                gc.scale_ctm(1./zoom, 1./zoom)
                gc.translate_ctm(-x*(1-zoom), -y*(1-zoom))

            self._render_primitive(gc, view_bounds, mode)

        return

    def _render_primitive(self, gc, view_bounds=None, mode='default'):
        raise NotImplementedError()

    def _text_default(self):
        # Disable text labels for now
        return ''

    def normal_left_down(self, event):
        # Disable mouse interaction for now
        return
