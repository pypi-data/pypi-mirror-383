from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Analysis.Base.AnalysisBase import AnalysisBase

class AnalysisFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Analysis', base_class=AnalysisBase)

    def configure(self, opts):
        super().configure(opts, 'analysis_name')
