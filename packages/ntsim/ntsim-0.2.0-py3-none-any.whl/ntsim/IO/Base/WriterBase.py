from ntsim.Base.BaseConfig import BaseConfig

from abc import ABC, abstractmethod
import numpy as np
from typing import Union, List, Iterable, Mapping
from ntsim.IO.Base.StructData import StructData, StructContainer

class WriterBase(BaseConfig):
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def __getitem__(self, path: str) -> "Directory":
        return Directory(self, path)

    @abstractmethod
    def write_data(self, group_path: str, label: str, data: np.ndarray):
        """Writes single array to specified path"""
        pass

    @abstractmethod
    def open(self):
        """Open the resources"""
        pass

    @abstractmethod
    def close(self):
        """Releases all resources"""
        pass


class Directory:
    def __init__(self, writer: WriterBase, path: str):
        self._writer = writer
        self.logger = self._writer.logger
        self._path = path

    def __getitem__(self, subgroup: str) -> "Directory":
        return Directory(self._writer, f"{self._path}/{subgroup}")

    def write(self, data):
        #filter the fields we want to write - if possible
        if hasattr(data, 'data2writer'):
            data = data.data2writer()
        # check if we have mapping 
        if isinstance(data, Mapping):
            for key,value in data.items():
                self[key].write(value)
        elif isinstance(data, list):
            data_dict = {str(n): val for n, val in enumerate(data)}
            self.write(data_dict)
        else: 
            #actually create the dataset
            path, label = self._path.rsplit('/',1)
            self._writer.write_data(path=path, label=label, data=data)
