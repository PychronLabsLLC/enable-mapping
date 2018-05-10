
from traits.api import Interface


class ITileManager(Interface):
    """
    Interface for tile source
    """

    def get_data_dimensions(self, zoom):
        """ Return the rows X columns dimension of the data at the given zoom
        level. zoom == -1 is a synonym for the maximum zoom level
        """

    def get_tile_size(self):
        """ Return size of tile
        """

    def get_tile(self, zoom, row, col):
        """ Request a tile at row and col for a particular zoom level
        """

    def get_wrap_flags(self):
        """ Return a tuple of booleans which indicate which axes should wrap
        infinitely.
        """

    def convert_to_tilenum(self, x, y, zoom):
        """ Convert screen space to a particular tile reference
        """
