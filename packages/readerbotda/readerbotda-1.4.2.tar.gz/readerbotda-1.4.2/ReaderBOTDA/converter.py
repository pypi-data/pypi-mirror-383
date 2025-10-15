from ReaderBOTDA.settings import parseSettingsDict, Settings
from ReaderBOTDA.reader import Profile
import h5py
from os import path
from glob import glob

def convert_to_h5(folder: str, putput_filename: str):

    filelist = glob(path.join(folder,'*.json'))

    if filelist:
        with h5py.File("mytestfile.hdf5", "w") as f:
            f.create_group("bfs")
            for file in filelist:
                temp = Profile(filename=file)
                