from ntsim.Analysis.Base.AnalysisBase import AnalysisBase
from ntsim.IO.gEvent import gEvent
import pandas as pd
import numpy as np

class SaveHitSumWithTime(AnalysisBase):
    """ Class to save hits summed for each OM and time interval to csv file """
    arg_dict = {
        'output_file_name': {'type': str, 'default': 'hits.csv', 'help': ''},
        'time_window':{'type': float, 'default': 2, 'help': 'lenght of time intervals, ns'}
    }
    
    def configure(self, opts):      
        super().configure(opts)       
        self.event_counter = 0
        self.event_hits = []
    
    def analysis(self, event: gEvent) -> None:
        hits = event.hits[0].get_named_data()
        hits_pd = pd.DataFrame(hits)
        
        group_by_uid = hits_pd.groupby('uid').mean()  
        geom = group_by_uid[['x_m', 'y_m', 'z_m']]

        time = hits_pd['time_ns']
        time_bin = pd.cut(time, bins=np.arange(time.min(), time.max(), self.time_window))
        
        final_data = pd.DataFrame()
        for om, omtab in hits_pd.groupby('uid'):
            om_data = omtab['phe'].groupby(time_bin, observed=True).sum()
            om_data = pd.DataFrame(om_data)
            om_data['uid'] = om
            om_data['x_m'] = geom.loc[om]['x_m']
            om_data['y_m'] = geom.loc[om]['y_m']
            om_data['z_m'] = geom.loc[om]['z_m']
            final_data = pd.concat([final_data, om_data])

        final_data['time_ns'] = final_data.index
        time_ns = []
        for c in final_data['time_ns']:
            time_ns.append(0.5*(c.left + c.right))
        final_data['time_ns'] = time_ns
            
        final_data['event'] = self.event_counter 
        self.event_counter += 1
        self.event_hits += [final_data]

    def save_analysis(self):
        hits_table = pd.concat(self.event_hits)
        hits_table.to_csv(self.output_file_name)
               