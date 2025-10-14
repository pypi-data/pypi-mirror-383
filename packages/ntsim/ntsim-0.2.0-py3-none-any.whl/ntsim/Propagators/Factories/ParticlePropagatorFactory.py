from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase

class ParticlePropagatorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Propagators.PrimaryPropagators', base_class=PropagatorBase)
    
    def configure(self, opts):
        super().configure(opts, 'particle_propagator_name')
