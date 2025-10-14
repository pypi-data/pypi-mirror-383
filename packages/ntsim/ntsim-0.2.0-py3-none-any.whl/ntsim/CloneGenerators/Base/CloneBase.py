import abc
from ntsim.Base.BaseConfig import BaseConfig

class CloneBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name

    @abc.abstractmethod
    def generate_cloned_photons(self, event):
        return 