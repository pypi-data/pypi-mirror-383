from ntsim.Base.BaseFactory import BaseFactory
from ntsim.MediumScatteringModels.Base.MediumScatteringModelBase import MediumScatteringModelBase

class MediumScatteringModelsFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.MediumScatteringModels', base_class=MediumScatteringModelBase)
    
    def configure(self, opts):
        super().configure(opts, 'medium_scattering_model_name')