import itertools
import math
import pathlib

import fsspec
import zarr


def get_files(store):
    zg = zarr.open(store)
    path = pathlib.Path(store)

    for name, array in zg.arrays():
        array_path = path / name
        sep = array.metadata.dimension_separator

        yield from map(
            lambda t: str(array_path / sep.join(t)),
            itertools.product(
                *[
                    map(str, range(math.ceil(shape / chunk)))
                    for shape, chunk in zip(array.shape, array.chunks)
                ]
            ),
        )

        yield str(array_path)

    yield str(path)


def remove(store):
    protocol = fsspec.utils.get_protocol(store)
    fs = fsspec.filesystem(protocol)

    for f in get_files(store):
        if fs.isfile(f):
            fs.rm_file(f)
        elif fs.isdir(f):
            # TODO: Properly attach zmetadata depending on Zarr format
            fs.rm(f, recursive=True, maxdepth=1)
