from ntsim.Analysis.Base.AnalysisBase import AnalysisBase
from ntsim.IO.gEvent import gEvent
import pandas as pd

class SaveHitSum(AnalysisBase):
    """ Class to save hits summed for each OM to csv file """
    arg_dict = {
        'output_file_name': {'type': str, 'default': 'hits.csv', 'help': ''}
    }
    
    def configure(self, opts):      
        super().configure(opts)       
        self.event_counter = 0
        self.event_hits = []
    
    def analysis(self, event: gEvent) -> None:
        hits = event.hits[0].get_named_data()
        hits_pd = pd.DataFrame(hits)
        group_by_uid = hits_pd.groupby('uid').mean()  
        group_by_uid['phe'] = hits_pd.groupby('uid')['phe'].sum()
        final_data = group_by_uid[['x_m', 'y_m', 'z_m', 'phe']]
        
        final_data['event'] = self.event_counter 
        self.event_counter += 1
        self.event_hits += [final_data]

    def save_analysis(self):
        hits_table = pd.concat(self.event_hits)
        hits_table.to_csv(self.output_file_name)
               