import abc
from ntsim.Base.BaseConfig import BaseConfig

class PropagatorBase(BaseConfig):
    def __init__(self, name: str):
        self._name = name
        self.logger.info(f'Initialized Propagator')
        
    @abc.abstractmethod
    def propagate(self, event):
        pass
