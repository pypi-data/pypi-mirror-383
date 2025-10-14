import abc
from ntsim.Base.BaseConfig import BaseConfig

class CherenkovBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self.logger.info("Initialized Cherenkov Generator")

    @abc.abstractmethod
    def generate(self, event):
        pass