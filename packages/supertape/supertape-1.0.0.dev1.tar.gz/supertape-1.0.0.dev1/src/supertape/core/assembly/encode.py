from __future__ import annotations

from supertape.core.basic.encode import BasicFileCompiler
from supertape.core.file.api import DataBlock, TapeFile


def create_assembly_file(filename: str, assembly_source: str, start_address: int = 16000) -> TapeFile:
    body: list[int] = []

    for line in assembly_source.splitlines():
        body += [len(line)] + [ord(c) for c in line]

    body += [0xFF]

    filename = BasicFileCompiler.cleanup_program_name(filename)
    filename_bytes: list[int] = [ord(filename[i]) if i < len(filename) else 0x20 for i in range(8)]

    head: DataBlock = DataBlock(
        type=0x00,
        body=filename_bytes
        + [0x05, 0x00, 0x01, (start_address & 0xFF00) >> 8, start_address & 0xFF, 0x00, 0x00],
    )

    foot: DataBlock = DataBlock(type=0xFF, body=[])

    blocks: list[DataBlock] = [head]

    while body:
        block_content: list[int] = body[:255]
        body = body[len(block_content) :]

        blocks.append(DataBlock(type=0x01, body=block_content))

    blocks.append(foot)

    return TapeFile(blocks=blocks)
