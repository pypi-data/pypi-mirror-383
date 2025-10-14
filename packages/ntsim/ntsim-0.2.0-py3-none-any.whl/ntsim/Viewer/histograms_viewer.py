from ntsim.Viewer.viewer_base import viewerbase
import numpy as np
import pyqtgraph as pg

from scipy.stats import binned_statistic
from scipy.special import gamma
from scipy.optimize import curve_fit

from particle import Particle
import ntsim.utils.pdg_colors as dict_colors
import ntsim.utils.systemofunits as units

import logging
log = logging.getLogger('histograms_viewer')

def _visit_all_widgets(widgets_dict:dict):
            for name,obj in widgets_dict.items():
                if isinstance(obj, dict):
                    yield from _visit_all_widgets(obj)
                else:
                    yield name, obj
                    
class histograms_viewer(viewerbase):
    def configure(self,opts):
        self.legend         = pg.LegendItem((80,60), offset=(-70,20), labelTextSize = '12pt')
        self.legend_hist    = {}
        self.hists_static   = {}
        self.hists_animated = {'longitudinal': {},
                               'angle_distribution': {},
                               'cross': { 'mean': {}, 'std': {} },
                               'departure_angle': { 'mean': {}, 'std': {} }
                               }
        self.fits           = {}
        self.graphs         = {}
        self.x_data         = {}
        self.x_bins         = {}
        self.x_data_profile = {}
        self.y_data_profile = {}

    def build_energy_histogram(self):
        primary_energy = np.array([self.data['tracks'][track]['E_tot_GeV'][0] for track in self.data['tracks']])
        hist = np.histogram(primary_energy[1:], bins=int(np.max(primary_energy[1:])/units.MeV))
        self.hists_static['primary_energy'] = self.widgets['primary_energy'].plot(x=hist[1], y=hist[0], stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
        self.widgets['primary_energy'].setLabel('left', 'Amount')
        self.widgets['primary_energy'].setLabel('bottom', 'Energy', units='GeV')
        log.info('energy histogram has been created')

    def build_particle_histogram(self):
        particle_tracks = self.data['legend']
        self.legend = pg.LegendItem((80,60), offset=(-70,20), labelTextSize = '12pt')
        self.legend.setParentItem(self.widgets['particle_legend'].graphicsItem())
        counter = 0
        for uid in particle_tracks[1:,-3:-1]:
            if uid[0] in dict_colors.pdg_colors:
                self.graphs[uid[0]] = pg.BarGraphItem(x=np.arange(1)+counter, height=uid[-1], width=1, brush=dict_colors.pdg_colors[uid[0]], pen='w', name=f'{Particle.from_pdgid(uid[0])}')
                self.widgets['particle_legend'].addItem(self.graphs[uid[0]])
                self.widgets['particle_legend'].setLabel('left', 'Amount')
                counter += 1
                self.legend.addItem(self.graphs[uid[0]], f'{Particle.from_pdgid(uid[0])}: {uid[1]}')
        log.info('tracks legend has been created')

    def get_t(self, pos):
        X0 = 0.3608 # radiation length in water in meters
#        r = data.r[0] # position of primary Cherenkov photons
        t = pos[:,2] / X0 # depth along the shower axis z in radiation lengths
        return t

    def cross_size(self, data):
        x, y = data.position_m[0][:,0], data.position_m[0][:,1]
        rho = np.sqrt(x**2 + y**2) # cross distance from the cascade Z-axis to the point of the initial Cherenkov photon
        return rho

    def departure_angle(self, data):
        dir_x, dir_y, dir_z = data.direction[0].T  # 0 is for the 1st step
        cos_theta = dir_z / np.sqrt(dir_x**2 + dir_y**2 + dir_z**2) # Cherenkov photon departure angle
        return cos_theta

    def build_cascade_longitudinal_distribution(self, vis):
        depth_t = self.get_t(self.data['photons'].position_m[0])
        t_bins = np.linspace(0,np.max(depth_t),100) # histogram bins
        ph_fraction = 0.001
        nph_full = len(depth_t) / ph_fraction
        hist = np.histogram(depth_t, bins=t_bins)
        bin_width = np.diff(hist[1])[0]
        xdata = (hist[1][1:] + hist[1][:-1]) / 2 # bin centers
        ydata = hist[0] / bin_width / ph_fraction
        yfit, norm, tmax, q, chi2 = self.fit(nph_full, xdata, ydata)
        self.hists_static['longitudinal'] = self.widgets['longitudinal'].plot(x=hist[1], y=ydata, stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
        self.fit_long_distr = self.widgets['longitudinal'].plot(x=xdata, y=yfit, pen=pg.mkPen(color='r'), brush=(255,0,0))
        self.widgets['longitudinal'].setLabel('left', 'Amount')
        self.widgets['longitudinal'].setLabel('bottom', 't', units='depth in radiation lengths')
        self.legend_hist = pg.LegendItem((80,60), offset=(-70,20), labelTextSize = '12pt')
        self.legend_hist.setParentItem(self.widgets['longitudinal'].graphicsItem())
        self.legend_hist.addItem(self.hists_static['longitudinal'], f'<div style="text-align: center"><span>chi2: {chi2:.2f}</span><br><span>N: {norm:.2f}</span><br><span>tmax: {tmax:.2f}</span><br><span>q: {q:.2f}</span></div>')
        self.hists_static['longitudinal'].setVisible(vis)
        log.info('cascade longitudinal distribution has been created')

    def build_cascade_longitudinal_distribution_animated(self, frame, vis):
        for f in self.hists_animated['longitudinal']:
            if f == frame:
                self.hists_animated['longitudinal'][f].setVisible(vis)
            else:
                self.hists_animated['longitudinal'][f].setVisible(False)
        # check if this frame is already computed
        if frame not in self.hists_animated['longitudinal']:
            if frame:
                time_tick = np.array([self.frames[frame]])
                t = self.data['photons'].time_ns[0]
                p = t.argsort()
                t_new = t[p]
                t_new = t_new[ t_new <= time_tick ]
                pos = ((self.data['photons'].position_m[0])[p])[:len(t_new)]
                depth_t = self.get_t(pos)
                t_bins = np.linspace(0,np.max(depth_t),100) # histogram bins
                ph_fraction = 0.001
                hist = np.histogram(depth_t, bins=t_bins)
                bin_width = np.diff(hist[1])[0]
                ydata = hist[0] / bin_width / ph_fraction
                self.hists_animated['longitudinal'][frame] = self.widgets['longitudinal'].plot(x=hist[1], y=ydata, stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
                self.widgets['longitudinal'].setLabel('left', 'Amount')
                self.widgets['longitudinal'].setLabel('bottom', 't', units='depth in radiation lengths')

    def build_cascade_cross_distribution(self):
        self.hists_static['cross'] = {}
        depth_t = self.get_t(self.data['photons'].position_m[0])
        p = depth_t.argsort()
        cross_size = self.cross_size(self.data['photons'])
        means_result = binned_statistic(depth_t[p], [cross_size[p], cross_size[p]**2], bins=50, statistic='mean')
        means, means2 = means_result.statistic
        standard_deviations = np.sqrt(means2 - means**2)
        bin_edges = means_result.bin_edges
        bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.
        self.hists_static['cross']['std'] = pg.ErrorBarItem(x=bin_centers, y=means, height=standard_deviations, beam=0.5)
        self.widgets['cross'].addItem(self.hists_static['cross']['std'])
        self.hists_static['cross']['mean'] = pg.ScatterPlotItem()
        self.hists_static['cross']['mean'].addPoints(x=bin_centers, y=means)
        self.widgets['cross'].setLabel('left', 'Rho', units='meters')
        self.widgets['cross'].setLabel('bottom', 't', units='depth in radiation lengths')
        self.widgets['cross'].addItem(self.hists_static['cross']['mean'])

    def build_departure_angle_distribution_old(self):
        depth_t = self.get_t(self.data['photons'])
        cher_cos = self.departure_angle(self.data['photons'])
        self.bg4 = pg.ScatterPlotItem()
        self.bg4.addPoints(x=depth_t, y=cher_cos)
        self.widgets['departure_angle'].setLabel('left', 'cos theta')
        self.widgets['departure_angle'].setLabel('bottom', 't', units='depth in radiation lengths')
        self.widgets['departure_angle'].addItem(self.bg4)

    def build_departure_angle_distribution(self):
        self.hists_static['departure_angle'] = {}
        depth_t = self.get_t(self.data['photons'])
        p = depth_t.argsort()
        depth_t_bins = np.linspace(depth_t[p][0], depth_t[p][-1], 101)
#        bin_centers = 0.5 * (depth_t_bins[:-1] + depth_t_bins[1:])
        cher_cos = self.departure_angle(self.data['photons'])
        means_result = binned_statistic(depth_t[p], [cher_cos[p], cher_cos[p]**2], bins=50, statistic='mean')
        means, means2 = means_result.statistic
        standard_deviations = np.sqrt(means2 - means**2)
        bin_edges = means_result.bin_edges
        bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.
        '''
        df = pd.DataFrame({'x': depth_t[p], 'y': cher_cos[p]})
        df['bin'] = np.digitize(depth_t[p], bins=depth_t_bins)
#        hist = np.histogram(depth_t[p], bins=depth_t_bins)
        binned = df.groupby('bin')
        result = binned['y'].agg(['mean', 'sem'])
        a = df['bin'].unique()
        new_bins = np.delete(np.arange(101), a-1)
        new_bin_centers = np.delete(bin_centers, new_bins)
#        bin_centers = 0.5 * (new_bin_centers[:-1] + new_bin_centers[1:])
        result['x'] = new_bin_centers
        self.bg4 = pg.ErrorBarItem(x=result['x'], y=result['mean'], height=result['sem'], beam=0.5)
        '''
        self.hists_static['departure_angle']['std'] = pg.ErrorBarItem(x=bin_centers, y=means, height=standard_deviations, beam=0.5)
        self.widgets['departure_angle'].addItem(self.hists_static['departure_angle']['std'])
        self.hists_static['departure_angle']['mean'] = pg.ScatterPlotItem()
        self.hists_static['departure_angle']['mean'].addPoints(x=bin_centers, y=means)
        self.widgets['departure_angle'].setLabel('left', 'cos theta')
        self.widgets['departure_angle'].setLabel('bottom', 't', units='depth in radiation lengths')
        self.widgets['departure_angle'].addItem(self.hists_static['departure_angle']['mean'])

    def fit_costh(self):
        pass

    def build_departure_angle_histogram(self):
        cher_cos = self.departure_angle(self.data['photons'])
        p = cher_cos.argsort()
        cos_bins = np.linspace(-1, 1, 100)
        hist = np.histogram(cher_cos[p], bins=cos_bins)
        ydata = hist[0]/(len(hist[0])*2*np.pi)
        self.hists_static['angle_distribution'] = self.widgets['angle_distribution'].plot(x=hist[1], y=ydata, stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
#        self.widgets['angle_distribution'].setLogMode(y=True)
        self.widgets['angle_distribution'].setLabel('left', 'Amount')
        self.widgets['angle_distribution'].setLabel('bottom', 'cos theta')

    def get_t_new(self, data):
        X0 = 0.3608 # radiation length in water in meters
        r = data.position_m[0]
        t = r[:,2] / X0 # depth along the shower axis z in radiation lengths
        return t

    def get_t_e_new(self, r):
        X0 = 0.3608 # radiation length in water in meters
        t = r / X0 # depth along the shower axis z in radiation lengths
        return t

    def get_t_h_new(self, r):
        X0 = 0.917 # radiation length in water in meters
        t = r / X0 # depth along the shower axis z in radiation lengths
        return t

    def cross_size_new(self, data):
        x, y = data.position_m[0][:,0], data.position_m[0][:,1]
        rho = np.sqrt(x**2 + y**2) # cross distance from the cascade Z-axis to the point of the initial Cherenkov photon
        return rho

    def departure_angle_new(self, data):
        dir_x, dir_y, dir_z = data.dir[0].T
        cos_theta = dir_z / np.sqrt(dir_x**2 + dir_y**2 + dir_z**2) # Cherenkov photon departure angle
        return cos_theta

    def build_histogram_static(self, widget_name, norm, title, x_label, y_label):
        hist = np.histogram(self.x_data[widget_name], bins=self.x_bins[widget_name])
        ydata = hist[0] / norm
        self.hists_static[widget_name] = self.widgets[widget_name].plot(x=hist[1], y=ydata, stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
        self.widgets[widget_name].setLabel('bottom', x_label)
        self.widgets[widget_name].setLabel('left', y_label)

    def configure_histogram(self, hist_type, widget_name):
        self.x_data[widget_name] = hist_type(self.data['photons'])
#        self.x_data[widget_name] = self.data['photons'].r[0][:,2]
        self.x_bins[widget_name] = np.linspace(np.min(self.x_data[widget_name]), np.max(self.x_data[widget_name]), 100) # histogram bins

    def f(self, t, norm, tmax, q):
        return norm / (gamma(q)*tmax) * (q*t/tmax*np.exp(-t/tmax))**q

    def fit(self, nph_full, x_data, y_data):
        fit = curve_fit(self.f, x_data, y_data, p0=(nph_full, 3, 1), bounds=([0.5*nph_full, 1, 0],[2.*nph_full, 12,100]))
        norm, tmax, q = fit[0]
        yfit = self.f(x_data, norm, tmax, q)
        y_data[y_data==0] = 1
        chi2 = np.sum((yfit-y_data)**2/y_data) / (len(y_data)-3)
        return yfit, norm, tmax, q, chi2

    '''
    def gamma_distribution(self, a, b, t):
        return t**(a-1) * np.exp(-t*b) / gamma(a)

    def f(self, x, norm, f, a_h, a_e, b_h, b_e):
        return norm * ((1 - f) * self.gamma_distribution(a_h, b_h, self.get_t_h_new(x)) + f * self.gamma_distribution(a_e, b_e, self.get_t_e_new(x)))

    def fit(self, widget_name, x_data, y_data):
        fit = curve_fit(self.f, x_data, y_data, p0=(len(self.x_data[widget_name]), 0.2, 3, 3, 1, 1), bounds=([0.5*len(self.x_data[widget_name]), 0, 1, 1, 0, 0],[2.*len(self.x_data[widget_name]), 1, 12, 12, 100, 100]))
        norm, f, a_h, a_e, b_h, b_e = fit[0]
        yfit = self.f(x_data, norm, f, a_h, a_e, b_h, b_e)
#        y_data[y_data==0] = 1
        chi2 = np.sum((yfit-y_data)**2/y_data) / (len(y_data)-3)
        return yfit, norm, f, a_h, a_e, b_h, b_e, chi2
    '''

    def build_fit(self, widget_name, nph_full):
        x_data, y_data = self.hists_static[widget_name].getData()
        bin_centers = (x_data[:-1] + x_data[1:])/2.
        y_fit, norm, tmax, q, chi2 = self.fit(nph_full, bin_centers, y_data)
#        y_fit = self.f(bin_centers, len(self.x_data[widget_name]), 0.2, 3, 3, 1, 1)
        self.fits[widget_name] = self.widgets[widget_name].plot(x=bin_centers, y=y_fit, pen=pg.mkPen(color='r'), brush=(255,0,0))
        self.legend_hist[widget_name] = pg.LegendItem((80,60), offset=(-70,20), labelTextSize = '12pt')
        self.legend_hist[widget_name].setParentItem(self.widgets[widget_name].graphicsItem())
        self.legend_hist[widget_name].addItem(self.hists_static[widget_name], f'<div style="text-align: center"><span>chi2: {chi2:.2f}</span><br><span>N: {norm:.2f}</span><br><span>tmax: {tmax:.2f}</span><br><span>q: {q:.2f}</span></div>')

    '''
    def build_fit(self, widget_name, nph_full):
        x_data, y_data = self.hists_static[widget_name].getData()
        bin_centers = (x_data[:-1] + x_data[1:])/2.
        y_fit, norm, tmax, q, chi2 = self.fit(nph_full, bin_centers, y_data)
        self.fits[widget_name] = self.widgets[widget_name].plot(x=bin_centers, y=y_fit, pen=pg.mkPen(color='r'), brush=(255,0,0))
        self.legend_hist[widget_name] = pg.LegendItem((80,60), offset=(-70,20), labelTextSize = '12pt')
        self.legend_hist[widget_name].setParentItem(self.widgets[widget_name].graphicsItem())
        self.legend_hist[widget_name].addItem(self.hists_static[widget_name], f'<div style="text-align: center"><span>chi2: {chi2:.2f}</span><br><span>N: {norm:.2f}</span><br><span>tmax: {tmax:.2f}</span><br><span>q: {q:.2f}</span></div>')
        return norm, tmax, q, chi2
    '''

    def build_cascade_longitudinal_distribution_new(self, place='down-right'):
        widget_name = place
        self.configure_histogram(self.get_t_new, widget_name)
        ph_fraction = 1
        nph_full = len(self.x_data[widget_name]) / ph_fraction
#        norm = np.diff(self.x_bins[widget_name])[0] * ph_fraction
        norm = np.diff(self.x_bins[widget_name])[0]
        if not norm: norm = 1
        title, x_label, y_label = '', 't (depth in radiation lengths)', 'Amount'
        self.build_histogram_static(widget_name, norm, title, x_label, y_label)
#        norm, tmax, q, chi2 = self.build_fit(widget_name, nph_full)
        self.build_fit(widget_name, nph_full)

    def build_departure_angle_histogram_new(self, place='up-right'):
        widget_name = place
        self.configure_histogram(self.departure_angle_new, widget_name)
        norm = len(self.x_data) * 4 * np.pi
        title, x_label, y_label = '', 'Amount', 'cos (theta)'
        self.build_histogram_static(widget_name, norm, title, x_label, y_label)

    def build_profile_static(self, widget_name, title, x_label, y_label):
        self.hists_static[widget_name] = {}
        means_result = binned_statistic(self.x_data_profile[widget_name], [self.y_data_profile[widget_name], self.y_data_profile[widget_name]**2], bins=50, statistic='mean')
        means, means2 = means_result.statistic
        standard_deviations = np.sqrt(means2 - means**2)
        bin_edges = means_result.bin_edges
        bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.
        self.hists_static[widget_name]['std'] = pg.ErrorBarItem(x=bin_centers, y=means, height=standard_deviations, beam=0.5)
        self.widgets[widget_name].addItem(self.hists_static[widget_name]['std'])
        self.hists_static[widget_name]['mean'] = pg.ScatterPlotItem()
        self.hists_static[widget_name]['mean'].addPoints(x=bin_centers, y=means)
        self.widgets[widget_name].setLabel('bottom', x_label)
        self.widgets[widget_name].setLabel('left', y_label)
        self.widgets[widget_name].setTitle(title)
        self.widgets[widget_name].addItem(self.hists_static[widget_name]['mean'])

    def configure_profile(self, profile_type_x, profile_type_y, widget_name):
        self.x_data_profile[widget_name] = profile_type_x(self.data['photons'])
        self.y_data_profile[widget_name] = profile_type_y(self.data['photons'])

    def build_cascade_cross_distribution_new(self, place='down-left'):
        widget_name = place
        self.configure_profile(self.get_t_new, self.cross_size_new, widget_name)
        title, x_label, y_label = '', 'Rho (meters)', 't (depth in radiation lengths)'
        self.build_profile_static(widget_name, title, x_label, y_label)

    def build_departure_angle_distribution_new(self, place='down-right'):
        widget_name = place
        self.configure_profile(self.get_t_new, self.departure_angle, widget_name)
        title, x_label, y_label = '', 'cos theta', 't (depth in radiation lengths)'
        self.build_profile_static(widget_name, title, x_label, y_label)

    def build_photons_spectrum(self, place='up-left'):
        if 'distributions' not in self.hists_static: self.hists_static['distributions'] = {}
        photons_energies = 197*1e-6 / self.data['photons'].wavelength_nm # hc = 197 MeV * fm 
        hist = np.histogram(photons_energies, bins=100)
        self.hists_static['distributions'][place] = self.widgets[place].plot(x=hist[1], y=hist[0], stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True )
        self.widgets[place].setLabel('left', 'Amount')
        self.widgets[place].setLabel('bottom', 'Energy', units='MeV')
        log.info('photons spectrum histogram has been created')

    def build_photons_direction(self, place='up-right'):
        if 'distributions' not in self.hists_static: self.hists_static['distributions'] = {}
        cos_theta = self.departure_angle(self.data['photons']) # Photons departure angle
        hist = np.histogram(cos_theta, bins=100)
        self.hists_static['distributions'][place] = self.widgets[place].plot(x=hist[1], y=hist[0], stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True )
        self.widgets[place].setLabel('left', 'Amount')
        self.widgets[place].setLabel('bottom', 'cos theta')
        log.info('photons angular distribution histogram has been created')
    
    def build_histogram_animated(self, widget_name, norm, title, x_label, y_label, frame, vis):
        for f in self.hists_animated[widget_name]:
            if f == frame:
                self.hists_animated[widget_name][f].setVisible(vis)
            else:
                self.hists_animated[widget_name][f].setVisible(False)
        # check if this frame is already computed
        if frame not in self.hists_animated[widget_name]:
            if frame:
                time_tick = np.array([self.frames[frame]])
                t = self.data['photons'].time_ns[0]
                p = t.argsort()
                t_new = t[p]
                t_new = t_new[ t_new <= time_tick ]
                x_data_frame = self.x_data[widget_name][p][:len(t_new)]
                hist = np.histogram(x_data_frame, bins=self.x_bins[widget_name])
                ydata = hist[0] / norm
                self.hists_animated[widget_name][frame] = self.widgets[widget_name].plot(x=hist[1], y=ydata, stepMode='center', fillLevel=0, fillOutline=True, brush=(0,0,255,150), clickable=True)
                self.widgets[widget_name].setLabel('bottom', x_label)
                self.widgets[widget_name].setLabel('left', y_label)

    def build_cascade_longitudinal_distribution_animated_new(self, frame, vis):
        widget_name = 'longitudinal'
        ph_fraction = 0.001
        nph_full = len(self.x_data[widget_name]) / ph_fraction
#        norm = np.diff(self.x_bins[widget_name])[0] * ph_fraction
        norm = 1
        title, x_label, y_label = '', 'Amount', 't (depth in radiation lengths)'
        self.build_histogram_animated(widget_name, norm, title, x_label, y_label, frame, vis)

    def build_departure_angle_histogram_new_animated(self, frame, vis):
        widget_name = 'angle_distribution'
        norm = len(self.x_data) * 4 * np.pi
        title, x_label, y_label = '', 'Amount', 'cos (theta)'
        self.build_histogram_animated(widget_name, norm, title, x_label, y_label, frame, vis)

    def build_profile_animated(self, widget_name, title, x_label, y_label, frame, vis):
        for f in self.hists_animated[widget_name]['mean']:
            if f == frame:
                self.hists_animated[widget_name]['mean'][f].setVisible(vis)
                self.hists_animated[widget_name]['std'][f].setVisible(vis)
            else:
                self.hists_animated[widget_name]['mean'][f].setVisible(False)
                self.hists_animated[widget_name]['std'][f].setVisible(False)
        # check if this frame is already computed
        if frame not in self.hists_animated[widget_name]['mean']:
            if frame:
                time_tick = np.array([self.frames[frame]])
                t = self.data['photons'].time_ns[0]
                p = t.argsort()
                t_new = t[p]
                t_new = t_new[ t_new <= time_tick ]
                means_result = binned_statistic(self.x_data_profile[widget_name][p][:len(t_new)], [self.y_data_profile[widget_name][p][:len(t_new)], self.y_data_profile[widget_name][p][:len(t_new)]**2], bins=50, statistic='mean')
                means, means2 = means_result.statistic
                standard_deviations = np.sqrt(means2 - means**2)
                bin_edges = means_result.bin_edges
                bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.
                self.hists_animated[widget_name]['std'][frame] = pg.ErrorBarItem(x=bin_centers, y=means, height=standard_deviations, beam=0.5)
                self.widgets[widget_name].addItem(self.hists_animated[widget_name]['std'][frame])
                self.hists_animated[widget_name]['mean'][frame] = pg.ScatterPlotItem()
                self.hists_animated[widget_name]['mean'][frame].addPoints(x=bin_centers, y=means)
                self.widgets[widget_name].setLabel('bottom', x_label)
                self.widgets[widget_name].setLabel('left', y_label)
                self.widgets[widget_name].addItem(self.hists_animated[widget_name]['mean'][frame])

    def build_cascade_cross_distribution_new_animated(self, frame, vis):
        widget_name = 'cross'
        title, x_label, y_label = '', 'Rho (meters)', 't (depth in radiation lengths)'
        self.build_profile_animated(widget_name, title, x_label, y_label, frame, vis)

    def build_departure_angle_distribution_new_animated(self, frame, vis):
        widget_name = 'departure_angle'
        title, x_label, y_label = '', 'cos theta', 't (depth in radiation lengths)'
        self.build_profile_animated(widget_name, title, x_label, y_label, frame, vis)

    def clean_static(self):
        for name, widget in _visit_all_widgets(self.hists_static):
            parent = widget.parentWidget()
            parent.removeItem(widget)
            if name in self.fits:
                #parent.removeItem(self.fits[name])
                #parent.removeItem(self.legend_hist[name])
                self.legend_hist[name].clear()
        self.hists_static = {}
        self.fits = {}
        self.legend_hist = {}
        for uid in self.graphs: # FIXME : Do it normally!
            self.widgets['particle_legend'].removeItem(self.graphs[uid])
            self.widgets['particle_legend'].removeItem(self.legend)
            self.legend.clear()
        self.graphs = {}

    def clean_animated(self):
        for name, widget in _visit_all_widgets(self.hists_animated):
            widget.parent.removeItem(widget)

        self.hists_animated = { 'longitudinal': {},
                                'angle_distribution': {},
                                'cross': { 'mean': {}, 'std': {} },
                                'departure_angle': { 'mean': {}, 'std': {} }
                                }

    def clean_view(self):
        self.clean_static()
        self.clean_animated()
        self.x_data = {}
        self.x_bins = {}
        self.x_data_profile = {}
        self.y_data_profile = {}

    def setVisible_hist_static(self, vis):
        for graph in self.hists_static.keys():
            if type(self.hists_static[graph]) is dict:
                for quantity in self.hists_static[graph]:
                    self.hists_static[graph][quantity].setVisible(vis)
            else:
                self.hists_static[graph].setVisible(vis)
                if graph in self.fits:
                    self.fits[graph].setVisible(vis)
                    self.legend_hist[graph].setVisible(vis)

    def setVisible_hist_animated(self, vis):
        for graph in self.hists_animated.keys():
            if self.hists_animated[graph].keys() == {'mean', 'std'}:
                for quantity in self.hists_animated[graph]:
                    for frame in self.hists_animated[graph][quantity]:
                        self.hists_animated[graph][quantity][frame].setVisible(vis)
            else:
                for frame in self.hists_animated[graph]:
                    self.hists_animated[graph][frame].setVisible(vis)

    def display_static(self, vis=False):
        if len(self.hists_static):
            self.setVisible_hist_static(vis)
            return
        if len(self.data['tracks']):
            self.build_energy_histogram()
            self.build_particle_histogram()
        
        if self.data['photons']:
            self.build_photons_spectrum(place='up-right')
            self.build_photons_direction(place='up-left')
            self.build_departure_angle_distribution_new(place='down-left')
            self.build_cascade_cross_distribution_new(place='down-right')
            # self.build_cascade_longitudinal_distribution_new(place='down-right')
        return
        

    def display_frame(self, frame, vis=False):
        return
        self.build_cascade_longitudinal_distribution_animated_new(frame, vis)
        self.build_departure_angle_histogram_new_animated(frame, vis)
        self.build_cascade_cross_distribution_new_animated(frame, vis)
        self.build_departure_angle_distribution_new_animated(frame, vis)
