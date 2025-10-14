from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase

class RayTracerFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Propagators.RayTracers', base_class=PropagatorBase)

    def configure(self, opts):
        super().configure(opts, 'ray_tracer_name')
