import gzip
from typing import Any, Iterator

from ..problem import Problem
from .reader import ExploreCallable, MoleculeEntry, Reader

__all__ = ["GzipReader"]


class GzipReader(Reader):
    def __init__(self) -> None:
        super().__init__()

    def read(self, input_stream: Any, explore: ExploreCallable) -> Iterator[MoleculeEntry]:
        if not hasattr(input_stream, "read") or not hasattr(input_stream, "seek"):
            raise TypeError("input must be a stream-like object")

        input_stream.seek(0)

        with gzip.open(input_stream, "rb") as f:
            # gzip.open will not raise an exception if the file is not a valid gzip file
            # --> check by attempting to read the first byte
            f.read(1)
            f.seek(0)

            try:
                yield from explore(f)
            except Exception as e:
                yield MoleculeEntry(
                    raw_input="<gzip>",
                    input_type="gzip",
                    source=("raw_input",),
                    mol=None,
                    errors=[Problem("invalid_input", f"Invalid gzip file: {e}")],
                )

    def __repr__(self) -> str:
        return "GzipReader()"
