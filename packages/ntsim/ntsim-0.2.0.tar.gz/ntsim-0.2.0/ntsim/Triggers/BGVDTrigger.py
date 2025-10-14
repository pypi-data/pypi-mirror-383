import numpy as np

from ntsim.Triggers.Base.TriggerBase import TriggerBase
from ntsim.IO.gEvent import gEvent

from ntsim.Triggers.Electronics.BGVDElectronics import BGVDElectronics
from ntsim.Triggers.TriggerConditions.BGVDTriggerConditions import BGVDTriggerConditions
from ntsim.utils.report_timing import report_timing

electronics_presets = {'default': BGVDElectronics(n_process=1),
                       'multiprocess': BGVDElectronics(n_process=None)}

trigger_presets = {'off': BGVDTriggerConditions(trigger_flag=False),
                  'default': BGVDTriggerConditions(),
                  'zero_limits': BGVDTriggerConditions(phe_limits=[0., 0.])}

class BGVDTrigger(TriggerBase):
    arg_dict = {'electronics_preset': {'type': str, 'choices': list(electronics_presets), 'default': 'default', 'help': ''},
                'trigger_preset': {'type': str, 'choices': list(trigger_presets), 'default': 'default', 'help': ''}}

    @report_timing
    def apply_trigger(self, event: gEvent):
        self.electronics = electronics_presets[self.electronics_preset]
        self.trigger_conditions = trigger_presets[self.trigger_preset] 
                
        hits = event.hits.get('Hits', None)
        if hits:
            ethits = self.electronics.apply_functions(hits)
            ethits = self.trigger_conditions.apply_functions(ethits)
            return ethits
        else:
            return None
