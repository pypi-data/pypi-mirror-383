from pathlib import Path
from typing import *
import os
import platform
import subprocess
import sys

import librosa

from audipart import AudioFile, AudioTrack, AudioTrackSeperator, AudioTrackVisualizer


REPOSITORY_DIR = Path(__file__).parent.parent.resolve()
RESOURCES_DIR = REPOSITORY_DIR / 'resources'


def main():
    if not (file_raw_path := select_file()):
        return

    src_file = Path(file_raw_path).resolve()
    audio = AudioFile.open(src_file)

    print(f'Opened Audio file: {audio}')

    dst_dir = src_file.with_name(src_file.stem)
    dst_dir.mkdir(exist_ok=True)

    print(f"Results will be saved at: '{dst_dir}'")

    seperator = AudioTrackSeperator(audio.tracks[0])
    tracks: List[AudioTrack] = []

    print(f'Adding Tracks')

    tracks.append(seperator.get_harmonic())
    tracks[-1].to_wav(dst_dir / (tracks[-1].name + '.wav'))

    tracks.append(seperator.get_percussive())
    tracks[-1].to_wav(dst_dir / (tracks[-1].name + '.wav'))

    for track in map(seperator.get_amplitude_by_midi,
                     reversed(range(int(librosa.note_to_midi('C1')),
                                    int(librosa.note_to_midi('C8'))+1))):
        tracks.append(track)
        tracks[-1].to_wav(dst_dir / (tracks[-1].name + '.wav'))

    print(f'Visualizing Tracks')

    visualizer = AudioTrackVisualizer(tracks=tracks)
    visualizer.plot(save_as=dst_dir / 'figure.png')

    print(f'Done.')

    open_dir(dst_dir)


def select_file() -> str:
    try:
        from PyQt5.QtWidgets import QApplication, QFileDialog
    except ImportError as e:
        raise ImportError(e.msg+'\nTry `pip install PyQt5`')

    app = QApplication(sys.argv)
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select an Audio file",
        RESOURCES_DIR.__fspath__(),
        "Audio Files (*.mp3 *.wav)",
    )
    return file_path


def open_dir(path: Path):
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")
    system = platform.system()
    if system == "Windows":
        os.startfile(path.__fspath__())  # type: ignore
    elif system == "Darwin":  # macOS
        subprocess.run(["open", path])
    elif system == "Linux":
        subprocess.run(["xdg-open", path])
    else:
        raise OSError(f"Unsupported Operating System: {system}")


main()
