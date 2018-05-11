from chaco.base_xy_plot import BaseXYPlot


class NullPlotRenderer(BaseXYPlot):
    """ A plot consisting of nothing.
    """

    def hittest(self, screen_pt, threshold=0.0, return_distance=False):
        return None

    def interpolate(self, index_value):
        return 0.0

    def get_screen_points(self):
        return []

    # -----------------------------------------------------------------------
    # Private methods; implements the BaseXYPlot stub methods
    # -----------------------------------------------------------------------

    def _render(self, gc, points):
        pass

    def _render_icon(self, gc, x, y, width, height):
        pass
