from typing import Any, Iterator

from rdkit.Chem import MolFromMolBlock

from ..polyfills import BlockLogs
from ..problem import Problem
from .reader import ExploreCallable, MoleculeEntry
from .stream_reader import StreamReader

__all__ = ["SdfReader"]


class SdfReader(StreamReader):
    def __init__(self, max_num_lines_mol_block: int = 100_000) -> None:
        super().__init__()
        self.max_num_lines_mol_block = max_num_lines_mol_block

    def _read_stream(self, input_stream: Any, explore: ExploreCallable) -> Iterator[MoleculeEntry]:
        # suppress RDKit warnings
        with BlockLogs():
            # We do not use SDMolSupplier, because it does not accept a stream-like
            # object as input. The ForwadSDMolSupplier is not suitable either, because
            # it does not allow to return the raw text.
            while True:
                # collect lines to parse as a mol block
                mol_block = ""
                num_lines = 0

                try:
                    line = input_stream.readline()
                except UnicodeDecodeError:
                    line = "<invalid_encoding>\n"

                while line:
                    mol_block += line
                    if line.strip() == "$$$$":
                        break

                    num_lines += 1
                    if num_lines > self.max_num_lines_mol_block:
                        break

                    # read next line
                    try:
                        line = input_stream.readline()
                    except UnicodeDecodeError:
                        line = "<invalid_encoding>\n"

                if mol_block.strip() != "":
                    try:
                        mol = MolFromMolBlock(mol_block, sanitize=False, removeHs=False)
                    except:  # noqa: E722 (allow bare except, because RDKit is unpredictable)
                        mol = None

                    if mol is None:
                        errors = [Problem("invalid_mol_block", "Invalid mol block")]
                    else:
                        errors = []

                    yield MoleculeEntry(
                        raw_input=mol_block.strip("\n"),
                        input_type="mol_block",
                        source=("raw_input",),
                        mol=mol,
                        errors=errors,
                    )

                # We stop reading if
                # (1) we have reached the end of the file OR
                # (2) the last entry had more than MAX_NUM_LINES_MOL_BLOCK lines
                #     (this entry is probably not a valid mol block and everything after
                #      it is probably not a valid mol block either)
                if (not line) or (num_lines > self.max_num_lines_mol_block):
                    break

    def __repr__(self) -> str:
        return f"SdfReader(max_num_lines_mol_block={self.max_num_lines_mol_block})"
