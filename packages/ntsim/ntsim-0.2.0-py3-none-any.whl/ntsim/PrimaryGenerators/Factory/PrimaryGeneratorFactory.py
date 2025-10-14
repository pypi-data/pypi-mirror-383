from ntsim.Base.BaseFactory import BaseFactory
from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase

class PrimaryGeneratorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.PrimaryGenerators', base_class=PrimaryGeneratorBase)
    
    def configure(self, opts):
        super().configure(opts, 'primary_generator_name')
