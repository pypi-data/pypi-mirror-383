from ntsim.Base.BaseFactory import BaseFactory
from ntsim.CherenkovGenerators.Base.CherenkovBase import CherenkovBase

class CherenkovGeneratorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.CherenkovGenerators', base_class=CherenkovBase)
    
    def configure(self, opts):
        super().configure(opts, 'cherenkov_generator_name')
