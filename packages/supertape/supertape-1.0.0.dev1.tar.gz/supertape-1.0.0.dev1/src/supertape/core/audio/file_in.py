import struct
import wave

from supertape.core.audio.api import AudioSignalListener
from supertape.core.audio.device import AUDIO_CHUNKSIZE


class FileInput:
    def __init__(self, filename: str, listeners: list[AudioSignalListener]) -> None:
        self._signallisteners: list[AudioSignalListener] = listeners
        self._filename: str = filename

    def run(self) -> None:
        wf: wave.Wave_read = wave.open(self._filename, "rb")

        while True:
            block = wf.readframes(AUDIO_CHUNKSIZE)

            buflen: int = len(block) // 2
            if buflen == 0:
                break

            format: str = f"{buflen}h"
            bytes: tuple[int, ...] = struct.unpack(format, block)

            for listener in self._signallisteners:
                listener.process_samples(bytes)

        wf.close()
