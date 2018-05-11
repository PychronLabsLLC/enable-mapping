from __future__ import print_function

import argparse
import math
import os
import os.path as op

import numpy as np
from PIL import Image

SIZE = 256


def store_chunks(array, dirpath):
    rows, cols = array.shape[:2]
    rows = rows // SIZE + 1
    cols = cols // SIZE + 1

    print('Writing:', dirpath)
    count = 0
    for r in range(rows):
        row_slice = slice(SIZE * r, SIZE * (r+1))
        for c in range(cols):
            col_slice = slice(SIZE * c, SIZE * (c+1))
            path = op.join(dirpath, '{}.{}.npy'.format(r, c))
            chunk = array[row_slice, col_slice, :]
            np.save(path, chunk, allow_pickle=False)
            count += 1
    print('Wrote', count, 'chunks')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    args = ap.parse_args()

    img = Image.open(args.file)
    if img.mode != 'RGB':
        print('nothing to do!')
        return

    array = np.array(img)

    max_dim = max(array.shape)
    num_lods = int(math.log(max_dim / SIZE, 2)) + 1
    if num_lods < 1:
        print('Not enough LOD levels')
        return

    for i, level in enumerate(range(num_lods, -1, -1)):
        path = op.join('lod', str(level))
        os.makedirs(path)

        step = 2 ** i
        store_chunks(array[::step, ::step, :], path)


if __name__ == '__main__':
    main()
