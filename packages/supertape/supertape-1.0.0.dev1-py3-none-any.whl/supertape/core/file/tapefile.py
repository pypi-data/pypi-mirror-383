import logging

from supertape.core.file.api import BlockListener, DataBlock, TapeFile, TapeFileListener, UnexpectedBlockType
from supertape.core.output.api import OutputStream
from supertape.core.output.streams import PrintOutputStream


class TapeFilePrinter(TapeFileListener):
    def __init__(self, stream: OutputStream | None = None) -> None:
        """Initialize the tape file printer.

        Args:
            stream: Output stream to write to. If None, uses PrintOutputStream.
        """
        self._stream = stream if stream is not None else PrintOutputStream()

    def process_file(self, file: TapeFile) -> None:
        self._stream.write("  +---------------------\\")
        self._stream.write("  |                     |\\")
        self._stream.write(f"  | File: {file.fname:>8s}      |_\\")
        self._stream.write(f"  | Size: {len(file.fbody):5d} bytes     |")
        self._stream.write(f"  | Type: {file.ftype:02X}h             |")
        self._stream.write(f"  | Data: {file.fdatatype:02X}h             |")
        self._stream.write(f"  |  Gap: {file.fgap:02X}h             |")
        self._stream.write("  |                       |")
        self._stream.write("  +-----------------------+")
        self._stream.write("")


class TapeFileLoader(BlockListener):
    def __init__(self, listeners: list[TapeFileListener]) -> None:
        self._listeners: list[TapeFileListener] = listeners
        self._blocks: list[DataBlock] = []
        self._logger: logging.Logger = logging.getLogger("file.tapefile")

    def process_block(self, block: DataBlock) -> None:
        if block.type == 0x00 and len(self._blocks) > 0:
            raise UnexpectedBlockType(block.type, 0)

        if block.type in [0x01, 0xFF] and len(self._blocks) == 0:
            raise UnexpectedBlockType(block.type, 0)

        self._blocks.append(block)

        if block.type == 0xFF:
            file = TapeFile(self._blocks)

            self._logger.debug("  +---------------------\\")
            self._logger.debug("  |                     |\\")
            self._logger.debug(f"  | File: {file.fname:>8s}      |_\\")
            self._logger.debug(f"  | Size: {len(file.fbody):5d} bytes     |")
            self._logger.debug(f"  | Type: {file.ftype:02X}h             |")
            self._logger.debug(f"  | Data: {file.fdatatype:02X}h             |")
            self._logger.debug(f"  |  Gap: {file.fgap:02X}h             |")
            self._logger.debug("  |                       |")
            self._logger.debug("  +-----------------------+")

            for listener in self._listeners:
                listener.process_file(file)

            self._blocks = []


class TapeFileSerializer(TapeFileListener):
    def __init__(self, listeners: list[BlockListener]) -> None:
        self._listeners: list[BlockListener] = listeners

    def process_file(self, file: TapeFile) -> None:
        for block in file.blocks:
            for listener in self._listeners:
                listener.process_block(block)
