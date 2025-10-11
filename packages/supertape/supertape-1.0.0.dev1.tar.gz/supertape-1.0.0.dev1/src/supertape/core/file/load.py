from __future__ import annotations

from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.block import BlockParser
from supertape.core.file.tapefile import TapeFileLoader


class _filelistener(TapeFileListener):
    def __init__(self) -> None:
        self.file: TapeFile | None = None

    def process_file(self, file: TapeFile) -> None:
        self.file = file


def file_load(file_name: str) -> TapeFile:
    with open(file_name, "rb") as tape_file:
        file_listener = _filelistener()
        tape_file_loader = TapeFileLoader([file_listener])
        block_parser = BlockParser([tape_file_loader])

        while True:
            byte: bytes = tape_file.read(1)

            if len(byte) == 0:
                break

            block_parser.process_byte(byte[0])

        if file_listener.file is None:
            raise ValueError("No tape file was loaded")
        return file_listener.file
