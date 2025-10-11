import argparse
import time
from typing import TextIO

from supertape.core.assembly.encode import create_assembly_file
from supertape.core.audio.signal_out import AudioPlayerObserver, AudioPlayerProgress
from supertape.core.basic.encode import BasicEncoder, BasicFileCompiler
from supertape.core.basic.minification import minify_basic
from supertape.core.basic.preprocess import preprocess_basic
from supertape.core.file.api import TapeFile
from supertape.core.file.play import play_file


def read_program(file: str) -> str:
    f: TextIO
    with open(file) as f:
        basic_source: str = f.read()

    return basic_source


def convert_program_to_tapefile(file_name: str, basic_code: str) -> TapeFile:
    file_compiler: BasicFileCompiler = BasicFileCompiler()
    encoder: BasicEncoder = BasicEncoder()

    instructions = [encoder.encode(line) for line in basic_code.splitlines()]
    outfile: TapeFile = file_compiler.compile_instructions(file_name, instructions)

    return outfile


def convert_assembly_program_to_tapefile(file_name: str, assembly_code: str) -> TapeFile:
    outfile: TapeFile = create_assembly_file(file_name, assembly_code)
    return outfile


class AudioObserver(AudioPlayerObserver):
    def __init__(self) -> None:
        self.complete: bool = False

    def on_progress(self, progress: AudioPlayerProgress) -> None:
        if progress.progress == progress.target:
            self.complete = True

    def wait_for_audio_completion(self) -> None:
        while not self.complete:
            time.sleep(0.5)

        time.sleep(0.5)


def play_tape(device: int | None, tape_file: TapeFile) -> None:
    obs: AudioObserver = AudioObserver()
    play_file(device=device, file=tape_file, observer=obs)
    obs.wait_for_audio_completion()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Play a local file to the audio interface."
    )
    parser.add_argument("--device", help="Select a device index.", type=int)
    parser.add_argument("file", type=str)
    args: argparse.Namespace = parser.parse_args()

    tape_file: TapeFile
    if args.file[-4:].lower() == ".bas":
        basic_code: str = read_program(args.file)
        basic_code = preprocess_basic(basic_code)
        basic_code = minify_basic(basic_code)
        tape_file = convert_program_to_tapefile(args.file, basic_code)
    elif args.file[-4:].lower() == ".asm":
        asm_code: str = read_program(args.file)
        tape_file = convert_assembly_program_to_tapefile(args.file, asm_code)

    play_tape(device=args.device, tape_file=tape_file)


if __name__ == "__main__":
    main()
