#####################################################################
# Data models
#####################################################################

from __future__ import annotations

from supertape.core.audio.api import AudioStreamError

FILE_TYPE_BASIC = 0x00
FILE_TYPE_MACHINE = 0x02
FILE_TYPE_DATA = 0x04
FILE_TYPE_ASMSRC = 0x05

FILE_DATA_TYPE_BIN = 0x00
FILE_DATA_TYPE_ASC = 0xFF

FILE_GAP_NONE = 0x00
FILE_GAP_GAPS = 0xFF


class DataBlock:
    def __init__(self, type: int, body: list[int]) -> None:
        self.type: int = type
        self.body: list[int] = body
        self.checksum: int = (type + len(body) + sum(body)) % 256

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "Block-" + hex(self.type) + "-" + str([hex(x) for x in self.body])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataBlock):
            return False
        return self.type == other.type and self.body == other.body


class TapeFile:
    def __init__(self, blocks: list[DataBlock]) -> None:
        self.blocks: list[DataBlock] = blocks

        self.fname: str = self._get_name()
        self.fbody: list[int] = self._get_body()
        self.ftype: int = self.blocks[0].body[10]
        self.fdatatype: int = self.blocks[0].body[11]
        self.fgap: int = self.blocks[0].body[12]
        self.fstartaddress: int = self.blocks[0].body[13] * 256 + self.blocks[0].body[14]
        self.floadaddress: int | None = (
            self.blocks[0].body[15] * 256 + self.blocks[0].body[16] if len(self.blocks[0].body) > 16 else None
        )

    def _get_name(self) -> str:
        fname = ""

        for b in self.blocks[0].body[0:8]:
            fname += chr(b)

        return fname.rstrip()

    def _get_body(self) -> list[int]:
        body: list[int] = []

        for block in self.blocks[1:-1]:
            body += block.body

        return body

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TapeFile):
            return False
        return self.blocks == other.blocks

    def __str__(self) -> str:
        return "TapeFile{" + self.fname + "}"


#####################################################################
# Error management
#####################################################################


class InvalidCRCError(AudioStreamError):
    pass


class InvalidBlockType(AudioStreamError):
    def __init__(self, type: int) -> None:
        super().__init__("Unknown type for Alice block: " + hex(type))

        self.type: int = type


class UnexpectedBlockType(AudioStreamError):
    def __init__(self, received_type: int, expected_type: int) -> None:
        super().__init__(
            "Received block type " + hex(received_type) + " while expecting type " + hex(expected_type)
        )

        self.received_type: int = received_type
        self.expected_type: int = expected_type


#####################################################################
# Event management interfaces
#####################################################################


class BlockListener:
    def process_block(self, block: DataBlock) -> None:
        pass


class ByteListener:
    def process_byte(self, value: int) -> None:
        pass

    def process_silence(self) -> None:
        pass


class TapeFileListener:
    def process_file(self, file: TapeFile) -> None:
        pass
