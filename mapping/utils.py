import os.path as op

import mapping

DATA_DIR = op.join(op.dirname(mapping.__file__), 'data')


def get_builtin_mbtiles_path():
    """ Return the location of the included MBTileManager data file.
    """
    return op.join(DATA_DIR, 'map.mbtiles')
