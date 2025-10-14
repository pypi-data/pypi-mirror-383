import abc

from ntsim.Base.BaseConfig import BaseConfig
from ntsim.IO.gHits import gHits

class AnalysisBase(BaseConfig):
    
    def __init__(self, label: str):
        self._label = label
    
    @abc.abstractmethod
    def analysis(self, hits: gHits):
        pass
    
    @abc.abstractmethod
    def save_analysis(self):
        pass