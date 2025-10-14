from collections import Counter

from ntsim.Analysis.Base.AnalysisBase import AnalysisBase
from ntsim.IO.gEvent import gEvent

class EffectiveVolume(AnalysisBase):
    arg_dict = {
        'analysis_file': {'type': str, 'default': 'analysis', 'help': ''},
        'analysis_dir': {'type': str, 'default': 'h5_output', 'help': ''}
    }
    
    def configure(self, opts):
        
        super().configure(opts)
        
        self.n_detected_events = 0
        self.event_weights = []
    
    def analysis(self, event: gEvent) -> None:
        
        for ahits in event.hits:
            if ahits.has_hits():
                self.n_detected_events += 1
                self.event_weights.append(event.EventHeader.event_weight)

    def save_analysis(self):
        
        weights_counter = Counter(self.event_weights)
        weights_string  = '\n'.join(['{}:{}'.format(wrd,freq) for wrd,freq in weights_counter.items()])
        
        with open(f'{self.analysis_dir}/{self.analysis_file}.dat', 'w') as f:
            f.write(f'{self.n_detected_events}\n'+weights_string)