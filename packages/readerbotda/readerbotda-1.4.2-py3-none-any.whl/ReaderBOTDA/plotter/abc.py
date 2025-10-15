from abc import ABC, abstractmethod
import numpy.typing as npt


class Plotter(ABC):

    @abstractmethod
    def single_plot(self, position, profile, title: str = None):
        pass

    @abstractmethod
    def multiple_plot(self, position, profiles, timestamps, title: str = ""):
        pass

    @abstractmethod
    def statistics(self, position, mean, std, title: str = ""):
        pass

    @abstractmethod
    def raw2d_plot(self, position, frequency, BGS, title: str = None):
        pass

    @abstractmethod
    def rawBGS_plot(
        self,
        frequency,
        BGS,
        positions_m: npt.ArrayLike,
        index: int = None,
        title: str = None,
    ):
        pass

    @abstractmethod
    def raw3d_plot(self, position, frequency, BGS, title: str = None):
        pass

    @abstractmethod
    def max_plot(self, position, max, title: str = None):
        pass

    @abstractmethod
    def max_stat_plot(self, max_mean, max_std, title: str = ""):
        pass
