from dataclasses import dataclass
from json import load
from typing import Dict, Union, Optional
from dacite import from_dict
from enum import Enum

class EstimationMode(str, Enum):
    WEIGHTED = 'Weighted Correlation'
    CORRELATION = 'Correlation'
    LORFIT = 'Lorentzian fitting'
    POLYFIT = 'Polyfit'

class DynamicRange(int, Enum):
    '''Dynamic Range della picoscope espresso in mV o V.'''
    mV10 = 0
    mV20 = 1
    mV50 = 2
    mV100 = 3
    mV200 = 4
    mV500 = 5
    V1 = 6
    V2 = 7
    V5 = 8
    V10 = 9
    V20 = 10

@dataclass
class Pulse:
    Width_ns: float
    RepRate_kHz: float
    Amplitude_V: float
    Offset_V: float
    EDFAoutput: float

    def __str__(self):
       return f"Width: {self.Width_ns} ns,\tRep Rate: {self.RepRate_kHz} kHz,\tAmplitude: {self.Amplitude_V} V,\tOffset: {self.Offset_V} V,\tEDFA Pump: {self.EDFAoutput} mA."

@dataclass
class Clock:
    Power: float
    StartMHz: float
    StopMHz: float
    StepMHz: int

    def __str__(self):
        return f"Power: {self.Power} dBm,\tStart Freq: {self.StartMHz} MHz,\tStop Freq: {self.StopMHz} MHz,\tStep Freq: {self.StepMHz} MHz."

@dataclass
class Scope:
    Offset: float
    Average: int
    DynamicRange: Union[int,DynamicRange]
    TriggerDelay_m: float
    TriggerLevel_V: float

    def __post_init__(self):
        self.DynamicRange = DynamicRange(self.DynamicRange)

    def __str__(self):
        return f"Averages: {self.Average},\tRange: {self.DynamicRange.name},\tOffset: {self.Offset} V,\tTrigger Delay: {self.TriggerDelay_m} m,\tTrigger Level: {self.TriggerLevel_V} V."

@dataclass
class Cable:
    Length: float
    RefractiveIndex: float
    CoeffStrainGHz: float
    CoeffTemperatureGHz: float
    ReferenceBFS_GHz: float

    def __str__(self):
        return f"Length: {self.Length} m,\tRefractive Index: {self.RefractiveIndex},\tStrain Coeff: {self.CoeffStrainGHz} GHz/microstrain,\tTemperature Coeff: {self.CoeffTemperatureGHz} GHz/°C,\tReference BFS: {self.ReferenceBFS_GHz} GHz."

@dataclass
class Brillouin:
    EstimationMode: Union[str,int,EstimationMode]
    SplineRes: float
    Subset: float
    RemoveBackground: bool
    RemovePulseGhost: bool
    CalibrationLength: float
    peak_2nd_thr: Optional[float]
    polyfit_lorFWHM: Optional[float]
    polyfit_prefilter_bw: Optional[float]
    polyfit_prefilter_taps: Optional[int]

    def __post_init__(self):
        if isinstance(self.EstimationMode, EstimationMode):
            pass
        self.EstimationMode = EstimationMode(self.EstimationMode)

    def __str__(self):
        if self.EstimationMode == EstimationMode.POLYFIT:
            additional_settings = f"Lorentzian FWHM: {self.polyfit_lorFWHM} MHz,\tPrefilter BW: {self.polyfit_prefilter_bw},\tPrefilter taps: {self.polyfit_prefilter_taps}."
        elif self.EstimationMode == EstimationMode.WEIGHTED:
            additional_settings = f"Spline Resolution: {self.SplineRes} MHz,\tSubset: {self.Subset} MHz,\t2nd peak thr: {self.peak_2nd_thr}."
        else:
            additional_settings = f"Spline Resolution: {self.SplineRes} MHz,\tSubset: {self.Subset} MHz,\t2nd peak thr: {self.peak_2nd_thr}."
        return f"Mode: {self.EstimationMode},\t{additional_settings}"

@dataclass
class Settings:
    Pulse: Pulse
    Clock: Clock
    Scope: Scope
    Cable: Cable
    Brillouin: Brillouin

    def __str__(self):
        return f"PULSE\t- {self.Pulse}\nCLOCK\t- {self.Clock}\nSCOPE\t- {self.Scope}\nCABLE\t- {self.Cable}\nBRILL\t- {self.Brillouin}"

def parseSettingsDict(dict: Dict) -> Settings:
    dict['Brillouin']['EstimationMode'] = dict['Brillouin'].pop('Estimation mode')
    dict['Brillouin']['CalibrationLength'] = dict['Brillouin'].pop('CalibrationLength(S)')
    if '2nd_peak_thr' in dict['Brillouin']:
        dict['Brillouin']['peak_2nd_thr'] = dict['Brillouin'].pop('2nd_peak_thr')
    return from_dict(data_class=Settings, data=dict)

if __name__ == '__main__':
    #filename='data/2021/profiles/2021-11-08_16-51-16.652_rawarray.json'
    filename='data/2023_09/rawarray/2023-09-26_10-33-20.210_rawarray.json'
    #filename='C:/Users/marbr/OneDrive/Cohaerentia/00 - Sensori/Brillouin/BOTDA/Misure/2023_12 - polyfit/gialla_15MHz/rawarray/2023-12-11_10-30-23.093_rawarray.json'
    with open(filename) as file:
        text = load(file)
    setting_test = text['Settings']
    settings = parseSettingsDict(setting_test)
    print(settings)