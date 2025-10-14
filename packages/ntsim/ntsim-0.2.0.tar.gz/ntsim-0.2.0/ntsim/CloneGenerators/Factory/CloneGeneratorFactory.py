from ntsim.Base.BaseFactory import BaseFactory
from ntsim.CloneGenerators.Base.CloneBase import CloneBase

class CloneGeneratorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.CloneGenerators', base_class=CloneBase)
    
    def configure(self, opts):
        super().configure(opts, 'clone_generator_name')
