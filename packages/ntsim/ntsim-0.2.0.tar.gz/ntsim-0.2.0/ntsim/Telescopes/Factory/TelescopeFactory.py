from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Telescopes.Base.BaseTelescope import BaseTelescope
#import ntsim.telescopes as telescopes_package

class TelescopeFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Telescopes', base_class=BaseTelescope)

    def configure(self, opts):
        super().configure(opts, 'telescope_name')
