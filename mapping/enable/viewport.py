
from numpy import array
from traits.api import (
    Instance, Bool, CList, Int, Property, Float, DelegatesTo, NO_COMPARE
)
from enable.viewport import Viewport
from enable.base import empty_rectangle, intersect_bounds

from canvas import MappingCanvas
from zoom import MappingZoomTool

class MappingViewport(Viewport):

    component = Instance(MappingCanvas)

    zoom_tool = Instance(MappingZoomTool)
    zoom_level = Int(0)

    # NOTE: `NO_COMPARE` is needed to make sure that the view position gets
    # refreshed after being disabled. This is mostly a quirk in the way this
    # component is being used in `canopy_data`.
    geoposition = CList([0.0, 0.0], comparison_mode=NO_COMPARE)

    latitude = Property(Float, depends_on='geoposition')
    longitude = Property(Float, depends_on='geoposition')

    tile_cache = DelegatesTo('component')
    min_level = Property(lambda self: self.tile_cache.min_level)
    max_level = Property(lambda self: self.tile_cache.max_level)

    draw_cross = Bool(True)

    def __init__(self, **traits):
        self.zoom_tool = MappingZoomTool(self)
        super(MappingViewport, self).__init__(
            horizontal_anchor='center',
            vertical_anchor='center',
            zoom_tool=self.zoom_tool,
            stay_inside=True,
            enable_zoom=True,
            **traits
        )
        self._update_component_view_bounds()

    def _get_latitude(self):
        return self.geoposition[0]
    def _set_latitude(self, val):
        self.geoposition[0] = val 

    def _get_longitude(self):
        return self.geoposition[1]
    def _set_longitude(self, val):
        self.geoposition[1] = val 

    def _component_bounds_updated(self, old, new):
        super(MappingViewport, self)._component_bounds_updated(old, new)
        # FIXME: This seems to be needed to make sure the zooming works
        # smoothly. If removed, zooming fails after a few levels.
        self._geoposition_changed(self.geoposition, self.geoposition)

    def _bounds_changed(self, old, new):
        super(MappingViewport, self)._bounds_changed(old, new)
        # FIXME: This seems to be needed to make sure we re-orient the view
        # after the a viewport resize. If removed, resizing the viewport
        # causes the display to refresh with the displayed points at a corner
        # or outside the viewport.
        self._geoposition_changed(self.geoposition, self.geoposition)

    def _geoposition_changed(self, old, new):
        if self.component is None:
            return
        # Update view position
        lat, lon = self.geoposition
        x, y = self.component._WGS84_to_screen(lat, lon, self.zoom_level)
        w, h = self.view_bounds
        self.view_position = [x - w/2., y - h/2.]

    def _handle_view_box_changed(self):
        """ Handle the case when the viewport has changed.
        """
        x, y = self.view_position
        w, h = self.view_bounds
        lat, lon = self.component._screen_to_WGS84(
            x + w/2., y + h/2., self.zoom_level
        )
        self.trait_set(geoposition=[lat, lon])

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        if self.draw_cross:
            x, y, width, height = view_bounds
            with gc:
                # draw +
                size = 10
                gc.set_stroke_color((0,0,0,1))
                gc.set_line_width(1.0)
                cx, cy = x+width/2., y+height/2.
                gc.move_to(cx, cy-size)
                gc.line_to(cx, cy+size)
                gc.move_to(cx-size, cy)
                gc.line_to(cx+size, cy)
                gc.stroke_path()
        super(MappingViewport, self)._draw_overlay(gc, view_bounds, mode)

    def _draw_mainlayer(self, gc, view_bounds=None, mode="normal"):
        # For now, ViewPort ignores the view_bounds that are passed in...
        # Long term, it should be intersected with the view_position to
        # compute a new view_bounds to pass in to our component.
        if self.component is not None:

            x, y = self.position
            view_x, view_y = self.view_position
            with gc: 
                # Clip in the viewport's space (screen space).  This ensures
                # that the half-pixel offsets we us are actually screen pixels,
                # and it's easier/more accurate than transforming the clip
                # rectangle down into the component's space (especially if zoom
                # is involved).
                gc.clip_to_rect(x-0.5, y-0.5,
                                self.width+1,
                                self.height+1)
    
                # There is a two-step transformation from the viewport's "outer"
                # coordinates into the coordinates space of the viewed component:
                # scaling, followed by a translation.
                if self.enable_zoom:
                    if self.zoom != 0:
                        gc.scale_ctm(self.zoom, self.zoom)
                        gc.translate_ctm(x/self.zoom - view_x, y/self.zoom - view_y)
                    else:
                        raise RuntimeError("Viewport zoomed out too far.")
                else:
                    gc.translate_ctm(x - view_x, y - view_y)
    
                # Now transform the passed-in view_bounds; this is not the same thing as
                # self.view_bounds!
                if view_bounds:
                    # Find the intersection rectangle of the viewport with the view_bounds,
                    # and transform this into the component's space.
                    clipped_view = intersect_bounds(self.position + self.bounds, view_bounds)
                    if clipped_view != empty_rectangle:
                        # clipped_view and self.position are in the space of our parent
                        # container.  we know that self.position -> view_x,view_y
                        # in the coordinate space of our component.  So, find the
                        # vector from self.position to clipped_view, then add this to
                        # view_x and view_y to generate the transformed coordinates
                        # of clipped_view in our component's space.
                        offset = array(clipped_view[:2]) - array(self.position)
                        new_bounds = ((offset[0]/self.zoom + view_x),
                                      (offset[1]/self.zoom + view_y),
                                      clipped_view[2] / self.zoom, clipped_view[3] / self.zoom)
                        # FIXME This is a bit hacky - i should pass in the zoom level
                        # to the draw function
                        self.component._zoom_level = self.zoom_level
                        self.component.draw(gc, new_bounds, mode=mode)
        return

