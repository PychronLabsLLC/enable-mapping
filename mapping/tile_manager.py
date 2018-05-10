
from traits.api import HasTraits, Event, Int, Callable, provides

from .i_tile_manager import ITileManager


@provides(ITileManager)
class TileManager(HasTraits):
    """
    Base class for tile managers
    """

    min_level = Int(0)
    max_level = Int(17)

    tile_ready = Event

    process_raw = Callable

    def get_data_dimensions(self, zoom):
        """ Return the rows X columns dimension of the data at the given zoom
        level. zoom == -1 is a synonym for the maximum zoom level
        """
        if zoom == -1:
            zoom = self.max_level
        limit = 2 ** zoom
        return limit, limit

    def get_tile_size(self):
        """ Return size of tile
        """
        return 256

    def get_tile(self, zoom, row, col):
        """ Request a tile at row and col for a particular zoom level
        """
        raise Exception()

    def get_wrap_flags(self):
        """ Return a tuple of booleans which indicate which axes should wrap
        infinitely.
        """
        # Maps can wrap in X, but not in Y
        return True, False

    def convert_to_tilenum(self, x, y, zoom):
        """ Convert screen space to a particular tile reference
        """
        raise Exception()
