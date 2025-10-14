from ntsim.Base.BaseFactory import BaseFactory
from ntsim.Triggers.Base.TriggerBase import TriggerBase

class TriggerFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.Triggers', base_class=TriggerBase)

    def configure(self, opts):
        super().configure(opts, 'trigger_name')
