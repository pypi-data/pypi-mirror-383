import argparse
import pprint
from typing import Any

import pyaudio
import tabulate


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="List all available audio devices.")
    parser.add_argument("-l", help="Extended device information.", action="store_true")
    args: argparse.Namespace = parser.parse_args()

    p: pyaudio.PyAudio = pyaudio.PyAudio()
    info: dict[str, Any] = p.get_host_api_info_by_index(0)
    device_count: int = info.get("deviceCount", 0)
    device_info: list[dict[str, Any]] = [
        p.get_device_info_by_host_api_device_index(0, i) for i in range(0, device_count)
    ]

    if args.l:
        d: dict[str, Any]
        for d in device_info:
            pprint.pprint(d)

    rows: list[list[Any]] = [
        [d["index"], d["name"], d["maxInputChannels"], d["maxOutputChannels"], d["defaultSampleRate"]]
        for d in device_info
    ]

    print(
        tabulate.tabulate(
            rows, headers=["Index", "Name", "Input Channels", "Output Channels", "Default Sample Rate"]
        )
    )


if __name__ == "__main__":
    main()
