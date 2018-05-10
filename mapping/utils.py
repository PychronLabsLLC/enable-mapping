import os.path as op

import pkg_resources


def get_builtin_mbtiles_path():
    """ Return the location of the included MBTileManager data file.
    """
    return pkg_resources.resource_filename('mapping',
                                           op.join('data', 'map.mbtiles'))
