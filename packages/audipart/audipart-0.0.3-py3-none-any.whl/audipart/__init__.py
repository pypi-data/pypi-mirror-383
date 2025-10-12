from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import *

from numpy.typing import NDArray
from matplotlib.axes import Subplot
import numpy as np
import matplotlib.pyplot as plt
import librosa



@dataclass
class AudioTrack:
    name: str
    amplitude: NDArray[np.float32]
    sample_rate: int  # 초당 샘플 수

    def __str__(self) -> str:
        return f'<AudiTrack:{self.name}>'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def duration(self) -> float:
        """Return the duration of audio in seconds."""
        return len(self.amplitude) / self.sample_rate

    def to_wav(self, save_as: Path) -> 'WavFile':
        try:
            import soundfile
        except ImportError as e:
            raise ImportError(e.msg+'\nTry `pip install soundfile`')
        else:
            soundfile.write(save_as, self.amplitude, self.sample_rate)
            return WavFile(save_as)

    def to_wav_like(self, src_file: Path) -> 'WavFile':
        dst_stem = src_file.stem+'-'+self.name
        dst_file = src_file.with_stem(dst_stem).with_suffix('.wav')
        return self.to_wav(dst_file)


class AudioFile:
    @staticmethod
    def open(file: Path):
        if file.suffix == '.mp3':
            return Mp3File(file)
        elif file.suffix == '.wav':
            return WavFile(file)
        raise NotImplementedError(
            f"Unsupported file type: {file.suffix}\n"
            f"Currently, only .mp3 and .wav files are supported."
        )

    file: Path

    def __init__(self, file: Union[str, Path]) -> None:
        self.file = Path(file).resolve()
        assert self.file.exists() and self.file.is_file()

    def __str__(self) -> str:
        return f"<AudioFile:'{self.file.__fspath__()}'>"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def tracks(self) -> List[AudioTrack]:
        raise NotImplementedError


class WavFile(AudioFile):
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file)
        assert self.file.suffix == '.wav'

    @property
    @lru_cache
    def tracks(self) -> List[AudioTrack]:
        y, sr = librosa.load(self.file)
        return [AudioTrack(name='raw', amplitude=y, sample_rate=int(sr))]


class Mp3File(AudioFile):
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file)
        assert self.file.suffix == '.mp3'

    @property
    @lru_cache
    def tracks(self) -> List[AudioTrack]:
        directory: Path
        with TemporaryDirectory(prefix='audipart') as tmp_dir:
            directory = Path(tmp_dir)
            file = directory / self.file.with_suffix('.wav').name
            return self.to_wav(file).tracks
        assert not directory.exists()

    def to_wav(self, save_as: Path) -> WavFile:
        try:
            from pydub import AudioSegment
        except ImportError as e:
            raise ImportError(e.msg+'\nTry `pip install pydub`')

        assert save_as.suffix == '.wav'
        audio = AudioSegment.from_mp3(self.file.__fspath__())
        audio.export(save_as.__fspath__(), format="wav")
        return WavFile(save_as)

    def to_wav_like(self) -> WavFile:
        return self.to_wav(self.file.with_suffix('.wav'))


class CQT:
    def __init__(self, track: AudioTrack, note_lo: str, note_hi: str, bins_per_octave: int) -> None:
        self.track = track
        self.note_lo = note_lo
        self.note_hi = note_hi
        self.bins_per_octave = bins_per_octave

    @property
    def n_octaves(self) -> int:
        return int(np.ceil((self.midi_hi - self.midi_lo + 1) / 12))

    @property
    def n_bins(self) -> int:
        return self.n_octaves * self.bins_per_octave

    @property
    def spectrums(self) -> List[NDArray[np.complex64]]:
        return self._get_spectrums()

    @property
    def midi_lo(self):
        return librosa.note_to_midi(self.note_lo)

    @property
    def midi_hi(self):
        return librosa.note_to_midi(self.note_hi)

    def get_spectrum_by_note(self, note: str) -> NDArray[np.complex64]:
        bin_index = self.get_bin_index(note)
        return self.spectrums[bin_index]

    def get_amplitude_by_note(self, note: str) -> NDArray[np.float32]:
        return self._get_amplitude_by_note_range(note, note)

    def get_amplitude_by_note_range(self, note_lo: str, note_hi: str) -> NDArray[np.float32]:
        return self._get_amplitude_by_note_range(note_lo, note_hi)

    def get_bin_index(self, note: str) -> int:
        midi = librosa.note_to_midi(note)
        index = (midi - self.midi_lo + 1) * (self.bins_per_octave // 12)
        assert 0 <= index < self.n_bins
        return int(index)

    @lru_cache
    def _get_spectrums(self) -> List[NDArray[np.complex64]]:
        return librosa.cqt(y=self.track.amplitude,  # type: ignore
                           sr=self.track.sample_rate,
                           fmin=librosa.note_to_hz(self.note_lo),
                           n_bins=self.n_bins,
                           bins_per_octave=self.bins_per_octave)

    def _get_amplitude_by_note_range(self, note_lo: str, note_hi: str) -> NDArray[np.float32]:
        idx_range = slice(
            max(self.get_bin_index(note_lo)-1, 0),
            min(self.get_bin_index(note_hi)+1,
                self.get_bin_index(self.note_lo)+self.n_bins-1),
        )
        spectrums = np.zeros_like(self.spectrums)
        spectrums[idx_range, :] = self.spectrums[idx_range, :]  # type: ignore
        return librosa.icqt(C=spectrums,
                            sr=self.track.sample_rate,
                            fmin=librosa.note_to_hz(self.note_lo),
                            bins_per_octave=self.bins_per_octave)


class AudioTrackSeperator:
    def __init__(self, track: AudioTrack) -> None:
        self.track = track

    def get_harmonic(self) -> AudioTrack:
        return AudioTrack(name='harmonic',
                          amplitude=self._apply_hpss()[0],
                          sample_rate=self.track.sample_rate)

    def get_percussive(self) -> AudioTrack:
        return AudioTrack(name='percussive',
                          amplitude=self._apply_hpss()[1],
                          sample_rate=self.track.sample_rate)

    def get_amplitude_by_midi(self, midi: int) -> AudioTrack:
        note = librosa.midi_to_note(midi)
        amplitude = self._apply_cqt().get_amplitude_by_note(note)
        return AudioTrack(name=note,
                          amplitude=amplitude,
                          sample_rate=self.track.sample_rate)

    def get_amplitude_by_note(self, note: str) -> AudioTrack:
        amplitude = self._apply_cqt().get_amplitude_by_note(note)
        return AudioTrack(name=note,
                          amplitude=amplitude,
                          sample_rate=self.track.sample_rate)

    def get_amplitude_by_note_range(self, note_lo: str, note_hi: str) -> AudioTrack:
        amplitude = self._apply_cqt().get_amplitude_by_note_range(note_lo, note_hi)
        return AudioTrack(name=f'{note_lo}..{note_hi}',
                          amplitude=amplitude,
                          sample_rate=self.track.sample_rate)

    @lru_cache
    def _apply_hpss(self) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
        harmonic, percussive = librosa.effects.hpss(self.track.amplitude,
                                                    kernel_size=43,
                                                    margin=3.0,
                                                    power=2.14)
        return harmonic, percussive

    @lru_cache
    def _apply_cqt(self) -> CQT:
        return CQT(track=self.get_harmonic(),
                   note_lo='C-1',
                   note_hi='C8',
                   bins_per_octave=36)


class AudioTrackVisualizer:
    def __init__(self, tracks: Iterable[AudioTrack]):
        self.tracks = list(tracks)
        self.fig_width_per_track = 256.
        self.fig_height_per_track = 4.
        self.ylabel_font_size = 64
        self.xlabel_font_size = 32

    def plot(self, save_as: Optional[Path] = None) -> None:
        n_tracks = len(self.tracks)
        figsize = (self.fig_width_per_track,
                   self.fig_height_per_track * n_tracks)
        plt.figure(figsize=figsize)
        for index, track in enumerate(self.tracks, start=1):
            subplot = plt.subplot(n_tracks, 1, index)
            self._plot_track(subplot, track)
        if save_as is None:
            plt.show()
        else:
            plt.savefig(save_as)

    def _plot_track(self, subplot: Subplot, track: AudioTrack):
        ticks: List[float] = [*np.arange(0, track.duration+5, 5)]
        xticks: List[float] = [t*track.sample_rate for t in ticks]
        xlabels: List[str] = [f'{int(t//60)}:{int(t%60):02d}' for t in ticks]
        subplot.plot(track.amplitude)
        subplot.set_ylabel(track.name, fontsize=self.ylabel_font_size,
                           rotation=0, ha='right')
        subplot.set_xticks(xticks, xlabels, fontsize=self.xlabel_font_size)
        subplot.set_xlim((0, track.amplitude.shape[0]))
        subplot.grid(True)
