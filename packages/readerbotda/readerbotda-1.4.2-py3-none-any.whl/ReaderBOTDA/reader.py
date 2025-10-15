from ReaderBOTDA.settings import parseSettingsDict, Settings
from ReaderBOTDA.plotter.abc import Plotter
from ReaderBOTDA.plotter.plotly import Plotly

from dataclasses import dataclass
from pathlib import Path
from json import load, loads
import numpy as np
import numpy.typing as npt
import h5py
from datetime import datetime, timezone  # TODO usare numpy anche per questo?
from os import path, PathLike, strerror
from glob import glob
from typing import Tuple, Union, Literal
import errno
import warnings
from progress.bar import Bar


class NoFilesSelected(Exception):
    def __init__(self, folder, message="No file found in folder"):
        self.message = f"{message}: {folder}"
        super().__init__(self.message)


# TODO da implementare nei metodi. E aggiungere anche i campi MaxMean e MaxStd
@dataclass
class Statistics:
    BFSmean: npt.ArrayLike
    BFSstd: npt.ArrayLike
    BFSstd_mean: float


class Profile:

    filename: str = ""
    plotter: Plotter
    settings: Settings
    sw_version: str = "<1.2.0.0"
    BFS: np.ndarray = np.array([])
    MaxGain: np.ndarray = np.array([])
    timestamp: datetime = datetime.now

    def __init__(
        self, filename: PathLike, plotter: Plotter = Plotly(), name: str = None
    ) -> None:
        """Load a single measure from a json file."""
        self.filename = filename
        self.plotter = plotter
        with open(self.filename) as file:
            text = load(file)
        self.settings = parseSettingsDict(text["Settings"])
        if "sw_version" in text:
            self.sw_version = text["sw_version"]
        if "sw_version" in text and text["sw_version"] == "":
            self.sw_version = "ambiente sviluppo"
        self.timestamp = datetime.strptime(
            text["Time Stamp"], "%Y-%m-%d" + "T" + "%H:%M:%S.%f" + "Z"
        )  # "2021-11-08T16:51:16.652Z"
        if not name:
            self.name = self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        else:
            self.name = name

        self.BFS = np.array(text["Profile"])
        self._createPositionArray()
        if "arrayMaxGain" in text:
            self.MaxGain = np.array(text["arrayMaxGain"])

    def _createPositionArray(self):
        self.position = np.linspace(
            0, self.settings.Cable.Length, num=len(self.BFS), endpoint=True
        )
        self.spatialResolution = self.position[1]

    def plot(self, title: str = None):
        if not title:
            title = self.name
        # TODO usare xrange espresso in metri per affettare array e poi passarli a single_plot. xrange:Tuple[float,float]=None
        return self.plotter.single_plot(self.position, self.BFS, title=title)

    def plotMax(self, title: str = None):
        if self.MaxGain.size == 0:
            warnings.warn(
                "Max array in not available. If possibile, load the raw file of the same measure."
            )
            return None
        if not title:
            title = self.name
        return self.plotter.max_plot(self.position, self.MaxGain, title)


class multipleProfile:

    statistics: Statistics
    plotter: Plotter

    def __init__(
        self,
        folder: PathLike,
        plotter: Plotter = Plotly(),
        n_measure: int = None,
        start_measure: Union[int, datetime] = 0,
        stop_measure: datetime = None,
    ):

        self.folder = folder
        self.plotter = plotter

        filelist = glob(path.join(folder, "*.json"))
        if start_measure and isinstance(start_measure, datetime):
            timestamps_files = [
                datetime.strptime(
                    "_".join(path.basename(file).split("_")[:2]), "%Y-%m-%d_%H-%M-%S.%f"
                )
                for file in filelist
            ]
            primo = next(
                (
                    x
                    for x, value in enumerate(timestamps_files)
                    if value >= start_measure
                ),
                0,
            )
            if stop_measure:
                ultimo = next(
                    (
                        x
                        for x, value in enumerate(timestamps_files)
                        if value > stop_measure
                    ),
                    len(filelist),
                )
            elif n_measure:
                ultimo = primo + n_measure
            else:
                ultimo = len(filelist)
            filelist = filelist[primo:ultimo]

        if n_measure and (start_measure == 0 or isinstance(start_measure, int)):
            filelist = filelist[start_measure : start_measure + n_measure]

        if isinstance(start_measure, int) and not n_measure and stop_measure:
            timestamps_files = [
                datetime.strptime(
                    "_".join(path.basename(file).split("_")[:2]), "%Y-%m-%d_%H-%M-%S.%f"
                )
                for file in filelist
            ]
            ultimo = next(
                (x for x, value in enumerate(timestamps_files) if value > stop_measure),
                len(filelist),
            )
            filelist = filelist[start_measure:ultimo]

        if len(filelist) == 0:
            raise NoFilesSelected(folder=folder)

        timestamps = list()
        with Bar("Redaing files", max=len(filelist)) as bar:
            for file in filelist:
                temp = Profile(filename=file)
                timestamps.append(temp.timestamp)
                try:
                    self.BFS = np.column_stack((self.BFS, temp.BFS))
                    self.MaxGain = np.column_stack((self.MaxGain, temp.MaxGain))
                except AttributeError:
                    self.BFS = temp.BFS
                    self.MaxGain = temp.MaxGain
                bar.next()

        self.timestamps = np.array(timestamps)
        self.settings = temp.settings
        self.sw_version = temp.sw_version
        self.position = temp.position
        self.calcStatistics()
        self.MaxGainMean = self.MaxGain.mean(axis=1)
        self.MaxGainStd = self.MaxGain.std(axis=1)

    def calcCorrelations(
        self,
        type: Literal["max", "bfs"],
        reference: Literal["first", "previous"] = "previous",
        range: Tuple[float, float] = None,
    ) -> np.array:
        """Ritorna correlazione tra prima misura e misura n-esima.
        Si può scegliere se effettuarla su matrice dei BFS o matrice dei massimi"""

        if type == "max":
            correlations = np.corrcoef(
                self.MaxGain[range[0] : range[1]] if range else self.MaxGain,
                rowvar=False,
            )
        else:
            correlations = np.corrcoef(
                self.BFS[range[0] : range[1]] if range else self.BFS, rowvar=False
            )

        if reference == "first":
            return correlations[0, :]

        indici = np.arange(1, np.shape(correlations)[0])
        return np.insert(correlations[indici, indici - 1], 0, 1)

    def calcStatistics(
        self, plot: bool = False, range: Tuple[float, float] = None, title: str = None
    ) -> Statistics:
        # TODO gestione input range
        self.statistics = Statistics(
            BFSmean=self.BFS.mean(axis=1),
            BFSstd=self.BFS.std(axis=1),
            BFSstd_mean=self.BFS.std(axis=1).mean(),
        )

        if plot:
            if not title:
                title = self.folder
            return self.plotter.statistics(
                self.position,
                self.statistics.BFSmean,
                self.statistics.BFSstd,
                title=title,
            )
        return self.statistics

    def deleteMeasures(self, indices: Union[int, list[int]]):
        """Delete measures from the dataset."""
        if isinstance(indices, int):
            indices = [indices]
        self.BFS = np.delete(self.BFS, indices, axis=1)
        self.MaxGain = np.delete(self.MaxGain, indices, axis=1)
        self.timestamps = np.delete(self.timestamps, indices)
        self.calcStatistics()

    def plotStatistics(self, title: str = None):
        if not title:
            title = self.folder
        # TODO se sono state calcolate con range allora position è sbagliato
        return self.plotter.statistics(
            self.position, self.statistics.BFSmean, self.statistics.BFSstd, title=title
        )

    def plot(
        self,
        startTime: datetime = datetime.min,
        stopTime: datetime = datetime.now(),
        title: str = None,
    ):
        if not title:
            title = self.folder
        match = [
            i
            for i, date in enumerate(self.timestamps)
            if date >= startTime and date <= stopTime
        ]
        return self.plotter.multiple_plot(
            self.position,
            self.BFS[:, match],
            [self.timestamps[i] for i in match],
            title=title,
        )

    def plotMax(self, title: str = None):
        if self.MaxGain.size == 0:
            warnings.warn(
                "Max array in not available. If possibile, load the raw file of the same measure."
            )
            return None
        if not title:
            title = self.folder
        return self.plotter.max_stat_plot(self.MaxGainMean, self.MaxGainStd, title)


class h5Profile(multipleProfile):

    def __init__(
        self,
        filename: PathLike,
        plotter: Plotter = Plotly(),
        # n_measure: int = None,
        # start_measure: Union[int, datetime] = 0,
        # stop_measure: datetime = None,
    ):
        """Load multiple measures from a h5 file."""
        self.filename = filename
        self.plotter = plotter

        if not path.isfile(filename):
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), filename)

        with h5py.File(filename, "r") as f:
            self.filename = filename
            self.folder = f.attrs["folder"]
            self.sw_version = f.attrs["sw_version"]

            self.position = f["position"][:]
            self.BFS = np.transpose(np.squeeze(f["data"]["bfs"][:]))
            self.MaxGain = np.transpose(np.squeeze(f["data"]["max_gain"][:]))
            self.timestamps = [
                datetime.fromtimestamp(timestamp / 1000000)  # FIXME, timezone.utc)
                for timestamp in f["data"]["timestamps"][:]
            ]
            self.settings = loads(
                f.attrs["settings"]
            )  # FIXME parseSettingsDict(loads(f.attrs["settings"]))

        self.calcStatistics()
        self.MaxGainMean = self.MaxGain.mean(axis=1)
        self.MaxGainStd = self.MaxGain.std(axis=1)


class Raw:

    filename: PathLike = Path("")
    plotter: Plotter
    settings: Settings
    sw_version: str = "<1.2.0.0"
    BGS: np.ndarray = np.array([])
    residuo: np.ndarray = np.array([])
    timestamp: datetime = datetime.now

    def __init__(self, filename: Union[str, Path], plotter: Plotter = Plotly()) -> None:
        """Load a single raw data from a json file."""
        self.filename = filename
        self.plotter = plotter
        with open(self.filename) as file:
            text = load(file)
        self.settings = parseSettingsDict(text["Settings"])
        if "sw_version" in text:
            self.sw_version = text["sw_version"]
        if "sw_version" in text and text["sw_version"] == "":
            self.sw_version = "ambiente sviluppo"
        self.BGS = np.transpose(np.array(text["Raw"]))
        self.timestamp = datetime.strptime(
            text["Time Stamp"], "%Y-%m-%d" + "T" + "%H:%M:%S.%f" + "Z"
        )  # "2021-11-08T16:51:16.652Z"
        self._createPositionArray()
        self._createFrequencyArray()
        try:
            self.residuo = np.array(text["residuo"])
        except KeyError:
            self.residuo = np.zeros(np.shape(self.frequency))

    def _createPositionArray(self) -> None:
        """Crea array numpy delle posizioni e la risoluzione spaziale"""
        self.position = np.linspace(
            0, self.settings.Cable.Length, num=self.BGS.shape[1], endpoint=True
        )
        self.spatialResolution = self.position[1]

    def _createFrequencyArray(self) -> None:
        """Crea array numpy delle frequenze, espresse in GHz"""
        self.frequency = (
            np.linspace(
                self.settings.Clock.StartMHz,
                self.settings.Clock.StartMHz
                + self.settings.Clock.StepMHz * self.BGS.shape[0],
                num=self.BGS.shape[0],
                endpoint=True,
            )
            / 1000
        )

    def plot2d(self, title: str = None):
        if not title:
            title = self.filename
        return self.plotter.raw2d_plot(
            self.position, self.frequency, self.BGS, title=title
        )

    def plot3d(self, title: str = None):
        if not title:
            title = self.filename
        return self.plotter.raw3d_plot(
            self.position, self.frequency, self.BGS, title=title
        )

    def plotBGS(self, index: int = None, title: str = None):
        """Plot 2D di tutti gli spettri BGS"""
        if not title:
            title = self.filename
        return self.plotter.rawBGS_plot(
            self.frequency,
            self.BGS,
            positions_m=self.position,
            index=index,
            title=title,
        )

    def plotMax(self, title: str = None):
        if not title:
            title = self.filename
        return self.plotter.max_plot(self.position, self.BGS.max(axis=0), title)


if __name__ == "__main__":
    """Non va se si lancia direttamente questo script a meno di non cambiare i primi due import da modules.settings a settings; uguale per plotter."""
    # a = Profile(filename='data/profiles/2021-11-08_16-51-16.652_rawarray.json')
    # b = multipleProfile(folder='data/profiles/')
    c = Raw(filename="data/raw/2021-11-08_16-51-16.652_rawmatrix.json")
    # print(b.BFS.shape)
