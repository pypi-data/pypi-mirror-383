from ntsim.Base.BaseFactory import BaseFactory
from ntsim.MediumProperties.Base.BaseMediumProperties import BaseMediumProperties

class MediumPropertiesFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.MediumProperties', base_class=BaseMediumProperties)

    def configure(self, opts):
        super().configure(opts, 'medium_properties_name')