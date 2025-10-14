from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Propagators.Base.PropagatorBase import PropagatorBase

class PhotonPropagatorFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Propagators.PhotonPropagators', base_class=PropagatorBase)

    def configure(self, opts):
        super().configure(opts, 'photon_propagator_name')
