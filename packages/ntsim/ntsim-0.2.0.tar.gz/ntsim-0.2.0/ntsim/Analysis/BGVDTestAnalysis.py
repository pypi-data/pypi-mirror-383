from collections import Counter

from ntsim.Analysis.Base.AnalysisBase import AnalysisBase
from ntsim.IO.gEvent import gEvent

class BGVDTestAnalysis(AnalysisBase):
    arg_dict = {
        'analysis_file': {'type': str, 'default': 'analysis', 'help': ''},
        'analysis_dir': {'type': str, 'default': 'h5_output', 'help': ''}
    }
    
    def configure(self, opts):
        
        super().configure(opts)
        
        self.n_triggered_event = 0
        self.triggered_events  = []
        self.detected_hits     = 0
    
    def analysis(self, event: gEvent) -> None:
        
        for ahits in event.hits:
            if ahits.has_hits():
                self.triggered_events.append(f'event_{self.n_triggered_event}')
                self.detected_hits += 1
        self.n_triggered_event += 1

    def save_analysis(self):
        
        with open(f'{self.analysis_dir}/{self.analysis_file}.dat', 'w') as f:
            f.write(f'Amount of triggered events: {self.detected_hits}\n'+'Triggered events:\n'+'\n'.join(self.triggered_events))