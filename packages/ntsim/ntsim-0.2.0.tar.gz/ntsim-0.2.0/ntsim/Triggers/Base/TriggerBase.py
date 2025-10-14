import abc
from ntsim.Base.BaseConfig import BaseConfig
from ntsim.IO.gHits import gHits

class TriggerBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self.logger.info("Initialized Trigger")

    @abc.abstractmethod
    def apply_trigger(self, event):
        pass