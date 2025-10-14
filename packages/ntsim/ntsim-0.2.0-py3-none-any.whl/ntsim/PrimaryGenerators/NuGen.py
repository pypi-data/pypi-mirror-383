import array
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lhapdf

from nudisxs.disxs import *
from particle import Particle
from scipy.integrate import quad, dblquad
from matplotlib import cm as colormap

import ntsim.utils.systemofunits as units

from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.utils.report_timing import report_timing
from ntsim.utils.pdg_constants import *
from ntsim.utils.gen_utils import resonance_decay
from ntsim.IO.gParticles import gParticles
from ntsim.random import rng

from time import time

class NuGen(PrimaryGeneratorBase):
    arg_dict = {'PDFSet':             {'type': str, 'default': 'CT18NNLO', 'help': ''},
                'energy_GeV':         {'type': float, 'default': 1000., 'help': ''},
                'energy_range_GeV':   {'type': float, 'nargs': 2, 'default': [100.,100.], 'help': ''},
                'position_m':         {'type': float, 'nargs': 3, 'type': float, 'default': [0.,0.,0.], 'help': ''},
                'cos_theta_range':    {'type': float, 'nargs': 2, 'default': [0.5,1.], 'help': ''},
                'cos_theta_bins':     {'type': int, 'default': 1000, 'help': ''},
                'phi_range':          {'type': float, 'nargs': 2, 'default': [0.,2*np.pi], 'help': ''},
                'phi_bins':           {'type': int, 'default': 1000, 'help': ''},
#                'target':             {'type': int, 'choices': (2212,2112), 'default': 2212, 'help': ''},
                'flavour_nu':         {'type': int, 'choices': (12,14,16,-12,-14,-16), 'default': 14, 'help': ''},
                'cross_section_mode': {'type': str, 'choices': ('calculate','nudisxs','data'), 'default': 'calculate', 'help': ''},
                'path_to_data':       {'type': str, 'default': './', 'help': ''},
                'current_mode':       {'type': str, 'choices': ('CC','NC'), 'default': 'CC', 'help': ''},
                'x_bins':             {'type': int, 'default': 10000, 'help': ''},
                'y_bins':             {'type': int, 'default': 10000, 'help': ''},
                'W_cut':              {'type': float, 'default': 1.2, 'help': ''},
                'save_data':          {'action': 'store_true', 'help': ''},
                'n_events':           {'type': int, 'default': 1, 'help': ''}}
    arg_dict.update(PrimaryGeneratorBase.arg_dict_position)

    def x_limits(self, W_cut, E_nu, f_nu):
        M = (self.m_N[2212]+self.m_N[2112])*0.5
        
        a = 1-((W_cut**2-M**2-self.m_l[f_nu]**2)*((W_cut**2-M**2)*E_nu+self.m_l[f_nu]**2*M))/(2*M*(W_cut**2-M**2)*E_nu**2)
        b = (1-((W_cut-self.m_l[f_nu])**2-M**2)/(2*M*E_nu))*(1-((W_cut+self.m_l[f_nu])**2-M**2)/(2*M*E_nu))
        c = 1+(W_cut**2-M**2-self.m_l[f_nu]**2)**2/(4*(W_cut**2-M**2)*E_nu**2)
        
        x_low = (a-np.sqrt(b))/(2*c)
        x_top = (a+np.sqrt(b))/(2*c)
        
        return x_low, x_top

    def y_limits(self, W_cut, E_nu, f_nu):
        M = (self.m_N[2212]+self.m_N[2112])*0.5
        
        y_low = lambda x: (1-self.m_l[f_nu]**2/(2*E_nu**2)*(1+(E_nu)/(M*x))-np.sqrt((1-self.m_l[f_nu]**2/(2*M*x*E_nu))**2-self.m_l[f_nu]**2/E_nu**2))/(2*(1+(M*x)/(2*E_nu)))
        y_top = lambda x: (1-self.m_l[f_nu]**2/(2*E_nu**2)*(1+(E_nu)/(M*x))+np.sqrt((1-self.m_l[f_nu]**2/(2*M*x*E_nu))**2-self.m_l[f_nu]**2/E_nu**2))/(2*(1+(M*x)/(2*E_nu)))
        
        y_cut = lambda x: (W_cut**2-M**2)/(2*M*(1-x)*E_nu)
        y_min = lambda x: np.max(np.column_stack([y_low(x),y_cut(x)]),axis=1)
        
        return y_min, y_top

    def configure(self, opts):
        
        super().configure(opts)
        
        self.pdfs = lhapdf.mkPDF(self.PDFSet)
        
        self.n_p_water  = 5/9
        self.n_n_water  = 4/9
        self.n_p_crust  = 0.5
        self.n_n_crust  = 0.5
        self.n_p_mantle = 24.974/50.192
        self.n_n_mantle = 25.218/50.192
        self.n_p_core   = 24.74/53.07
        self.n_n_core   = 28.33/53.07
        
        self.target_nucleon = {2212: 'proton', 2112: 'neutron'}
        self.m_N = {2212: m_p, 2112: m_n}
        self.m_l = {12: m_e, 14: m_mu, 16: m_tau, -12: m_e, -14: m_mu, -16: m_tau}
        self.f_l = {12: 11, 14: 13, 16: 15, -12: -11, -14: -13, -16: -15}
        
        Q = lambda x, y, E_nu, tar: np.sqrt(2*self.m_N[tar]*x*y*E_nu)

        self.d    = {2212: lambda x, y, E_nu, tar: self.pdfs.xfxQ(1, x, Q(x,y,E_nu,tar)),
                     2112: lambda x, y, E_nu, tar: self.pdfs.xfxQ(2, x, Q(x,y,E_nu,tar))}
        self.u    = {2212: lambda x, y, E_nu, tar: self.pdfs.xfxQ(2, x, Q(x,y,E_nu,tar)),
                     2112: lambda x, y, E_nu, tar: self.pdfs.xfxQ(1, x, Q(x,y,E_nu,tar))}
        self.s    = lambda x, y, E_nu, tar: self.pdfs.xfxQ(3, x, Q(x,y,E_nu,tar))
        self.c    = lambda x, y, E_nu, tar: self.pdfs.xfxQ(4, x, Q(x,y,E_nu,tar))
        self.b    = lambda x, y, E_nu, tar: self.pdfs.xfxQ(5, x, Q(x,y,E_nu,tar))
        self.dbar = {2212: lambda x, y, E_nu, tar: self.pdfs.xfxQ(-1, x, Q(x,y,E_nu,tar)),
                     2112: lambda x, y, E_nu, tar: self.pdfs.xfxQ(-2, x, Q(x,y,E_nu,tar))}
        self.ubar = {2212: lambda x, y, E_nu, tar: self.pdfs.xfxQ(-2, x, Q(x,y,E_nu,tar)),
                     2112: lambda x, y, E_nu, tar: self.pdfs.xfxQ(-1, x, Q(x,y,E_nu,tar))}
        self.sbar = lambda x, y, E_nu, tar: self.pdfs.xfxQ(-3, x, Q(x,y,E_nu,tar))
        self.cbar = lambda x, y, E_nu, tar: self.pdfs.xfxQ(-4, x, Q(x,y,E_nu,tar))
        self.bbar = lambda x, y, E_nu, tar: self.pdfs.xfxQ(-5, x, Q(x,y,E_nu,tar))
        
        self.s_0 = lambda x, y, E_nu, tar: G_F**2/(2*np.pi)*(self.m_N[tar]**2+2*self.m_N[tar]*E_nu)*(1+Q(x,y,E_nu,tar)**2/m_W**2)**(-2)*GeV2cm**(-2)
        
        
        cos_theta_nu = rng.uniform(low=self.cos_theta_range[0],high=self.cos_theta_range[1],size=opts.n_events)
        sin_theta_nu = np.sqrt(1.-cos_theta_nu**2)
        phi_nu       = rng.uniform(low=self.phi_range[0],high=self.phi_range[1],size=opts.n_events)
        self.P_nu = np.array([self.energy_GeV*sin_theta_nu*np.cos(phi_nu),
                              self.energy_GeV*sin_theta_nu*np.sin(phi_nu),
                              self.energy_GeV*cos_theta_nu]).T
        
        if self.random_position:
            self.position_m, self.weight = self.set_random_position(opts.n_events,self.random_volume)
        else:
            position_m = np.array(self.position_m)
        
        gamma_1 = rng.random(size=opts.n_events)
        
        n_crust = len(self.position_m[self.position_m[:,2]<0])
        n_water = opts.n_events-n_crust
        
        p_p_target = np.cumsum([self.n_p_crust,self.n_n_crust])
        p_n_target = np.cumsum([self.n_p_water,self.n_n_water])
        p_target = np.array([p_p_target]*n_crust+[p_n_target]*n_water)
        
        self.target = np.empty(shape=opts.n_events,dtype=int)
        for n, p_tar in enumerate(p_target):
            if gamma_1[n] < p_tar[0]: self.target[n] = 2212
            else: self.target[n] = 2112
        print('=========================: ', self.cross_section_mode)
        if self.cross_section_mode == 'calculate':
            
            x_low, x_top = self.x_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            y_low, y_top = self.y_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            
            x_min = np.min(x_low)
            x_max = np.max(x_top)
            y_min = np.min(y_low(x_min))
            y_max = np.max(y_top(x_max))
            
#            xs = np.linspace(x_min, x_max, num=self.x_bins)
            nxs = np.linspace(np.log10(x_min), np.log10(x_max), num=self.x_bins)
            xs = 10**nxs
            ys = np.linspace(y_min, y_max, num=self.y_bins)
            
            xx, yy = np.meshgrid(xs, ys)
            
            if self.current_mode == 'CC':
                if self.flavour_nu > 0:
                    dis_p = self.d2s_xy_nu_CC(xx, yy, [self.energy_GeV], 2212, y_low, y_top)
                    dis_n = self.d2s_xy_nu_CC(xx, yy, [self.energy_GeV], 2112, y_low, y_top)
                else:
                    dis_p = self.d2s_xy_anu_CC(xx, yy, [self.energy_GeV], 2212, y_low, y_top)
                    dis_n = self.d2s_xy_anu_CC(xx, yy, [self.energy_GeV], 2112, y_low, y_top)
            elif self.current_mode == 'NC':
                if self.flavour_nu > 0:
                    dis_p = self.d2s_xy_nu_NC(xx, yy, [self.energy_GeV], 2212, y_low, y_top)
                    dis_n = self.d2s_xy_nu_NC(xx, yy, [self.energy_GeV], 2112, y_low, y_top)
                else:
                    dis_p = self.d2s_xy_anu_NC(xx, yy, [self.energy_GeV], 2212, y_low, y_top)
                    dis_n = self.d2s_xy_anu_NC(xx, yy, [self.energy_GeV], 2112, y_low, y_top)
            if self.save_data:
                np.savez(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2212}', dis_p, xx, yy)
                np.savez(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2112}', dis_n, xx, yy)
        elif self.cross_section_mode == 'nudisxs':
            
            dis = disxs()
            
            x_low, x_top = self.x_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            y_low, y_top = self.y_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            
            x_min = np.min(x_low)
            x_max = np.max(x_top)
            y_min = np.min(y_low(x_min))
            y_max = np.max(y_top(x_max))
            
            #xs = np.linspace(x_min, x_max, num=self.x_bins)
            nxs = np.linspace(np.log10(x_min), np.log10(x_max), num=self.x_bins)
            xs = 10**nxs
            ys = np.linspace(y_min, y_max, num=self.y_bins)
            
            xx, yy = np.meshgrid(xs, ys)
            
            dis.init_neutrino(self.flavour_nu)
            dis.init_pdf(self.PDFSet)
            dis.init_target('proton')
            dis_p = dis.xs_nc_as_array(np.array([self.energy_GeV]), xs, ys)
#            dis_p = dis.xs_cc_as_array(np.array([self.energy_GeV]), xs, ys)
            dis.init_target('neutron')
            dis_n = dis.xs_nc_as_array(np.array([self.energy_GeV]), xs, ys)
#            dis_n = dis.xs_cc_as_array(np.array([self.energy_GeV]), xs, ys)
            if self.save_data:
                np.savez(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2212}', dis_p, xx, yy)
                np.savez(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2112}', dis_n, xx, yy)
        elif self.cross_section_mode == 'data':
            data_p = np.load(f'{self.path_to_data}' + f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2212}.npz')
            data_n = np.load(f'{self.path_to_data}' + f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{2112}.npz')
            dis_p, xx, yy = data_p['arr_0'], data_p['arr_1'], data_p['arr_2']
            dis_n = data_n['arr_0']
        
        self.dis = {2212: dis_p, 2112: dis_n}
        
        n_p = np.where(self.target==2212)[0]
        n_n = np.where(self.target==2112)[0]
        x_p, y_p = self.generate_xy(self.dis[2212], xx, yy, len(n_p))
        x_n, y_n = self.generate_xy(self.dis[2112], xx, yy, len(n_n))
        '''
        fig, ax = plt.subplots(2)
        
        hist_x, bin_edges_x = np.histogram(x_p,bins=1000,density=True)
        ax[0].stairs(hist_x, bin_edges_x)
        ax[0].minorticks_on()
        ax[0].set_axisbelow(True)
        ax[0].grid(which='major')
        ax[0].grid(which='minor',linestyle=':')
        ax[0].set_xlabel('x')
        
        hist_y, bin_edges_y = np.histogram(y_p,bins=1000,density=True)
        ax[1].stairs(hist_y, bin_edges_y)
        ax[1].minorticks_on()
        ax[1].set_axisbelow(True)
        ax[1].grid(which='major')
        ax[1].grid(which='minor',linestyle=':')
        ax[1].set_xlabel('y')
        
        plt.show()
        '''
        self.x = np.empty(shape=opts.n_events)
        self.y = np.empty(shape=opts.n_events)
        '''
        self.x[np.where(self.target==2212)] = x_p
        self.x[np.where(self.target==2112)] = x_n
        self.y[np.where(self.target==2212)] = y_p
        self.y[np.where(self.target==2112)] = y_n
        '''
        for i, idx in enumerate(n_p):
            self.x[idx]=x_p[i]
            self.y[idx]=y_p[i]
        for i, idx in enumerate(n_n):
            self.x[idx]=x_n[i]
            self.y[idx]=y_n[i]
        
        self.n_event = 0
    
    def d2s_xy_nu_CC(self, xx, yy, E_nu, tar, y_low, y_top):
        data = np.empty(shape=(len(E_nu),*np.shape(xx)))
        for n_ene, ene in enumerate(E_nu):
            for i in range(np.shape(xx)[0]):
                for j in range(np.shape(xx)[1]):
                    if yy[i,j] < y_low(xx[i,j]) or yy[i,j] > y_top(xx[i,j]):
                        data[n_ene,i,j] = 0
                    else:
                        data[n_ene,i,j] = 2*self.s_0(xx[i,j],yy[i,j],ene,tar)*(self.d[tar](xx[i,j],yy[i,j],ene,tar)+self.s(xx[i,j],yy[i,j],ene,tar)+ \
                                          (1-yy[i,j])**2*(self.ubar[tar](xx[i,j],yy[i,j],ene,tar)+self.cbar(xx[i,j],yy[i,j],ene,tar)))
        return data
    
    def d2s_xy_anu_CC(self, xx, yy, E_nu, tar, y_low, y_top):
        data = np.empty(shape=(len(E_nu),*np.shape(xx)))
        for n_ene, ene in enumerate(E_nu):
            for i in range(np.shape(xx)[0]):
                for j in range(np.shape(xx)[1]):
                    if yy[i,j] < y_low(xx[i,j]) or yy[i,j] > y_top(xx[i,j]):
                        data[n_ene,i,j] = 0
                    else:
                        data[n_ene,i,j] = 2*self.s_0(xx[i,j],yy[i,j],ene,tar)*(self.dbar[tar](xx[i,j],yy[i,j],ene,tar)+self.sbar(xx[i,j],yy[i,j],ene,tar)+ \
                                          (1-yy[i,j])**2*(self.u[tar](xx[i,j],yy[i,j],ene,tar)+self.c(xx[i,j],yy[i,j],ene,tar)))
        return data

    def d2s_xy_nu_NC(self, xx, yy, E_nu, tar, y_low, y_top):
        data = np.empty(shape=(len(E_nu),*np.shape(xx)))
        for n_ene, ene in enumerate(E_nu):
            for i in range(np.shape(xx)[0]):
                for j in range(np.shape(xx)[1]):
                    if yy[i,j] < y_low(xx[i,j]) or yy[i,j] > y_top(xx[i,j]):
                        data[n_ene,i,j] = 0
                    else:
                        data[n_ene,i,j] = 2*self.s_0(xx[i,j],yy[i,j],ene,tar)*((gU_L**2+(1-yy[i,j])**2*gU_R**2)*(self.u[tar](xx[i,j],yy[i,j],ene,tar)+self.c(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gD_L**2+(1-yy[i,j])**2*gD_R**2)*(self.d[tar](xx[i,j],yy[i,j],ene,tar)+self.s(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gU_R**2+(1-yy[i,j])**2*gU_L**2)*(self.ubar[tar](xx[i,j],yy[i,j],ene,tar)+self.cbar(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gD_R**2+(1-yy[i,j])**2*gD_L**2)*(self.dbar[tar](xx[i,j],yy[i,j],ene,tar)+self.sbar(xx[i,j],yy[i,j],ene,tar)))
        return data
    
    def d2s_xy_anu_NC(self, xx, yy, E_nu, tar, y_low, y_top):
        data = np.empty(shape=(len(E_nu),*np.shape(xx)))
        for n_ene, ene in enumerate(E_nu):
            for i in range(np.shape(xx)[0]):
                for j in range(np.shape(xx)[1]):
                    if yy[i,j] < y_low(xx[i,j]) or yy[i,j] > y_top(xx[i,j]):
                        data[n_ene,i,j] = 0
                    else:
                        data[n_ene,i,j] = 2*self.s_0(xx[i,j],yy[i,j],ene,tar)*((gU_R**2+(1-yy[i,j])**2*gU_L**2)*(self.u[tar](xx[i,j],yy[i,j],ene,tar)+self.c(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gD_R**2+(1-yy[i,j])**2*gD_L**2)*(self.d[tar](xx[i,j],yy[i,j],ene,tar)+self.s(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gU_L**2+(1-yy[i,j])**2*gU_R**2)*(self.ubar[tar](xx[i,j],yy[i,j],ene,tar)+self.cbar(xx[i,j],yy[i,j],ene,tar))+ \
                                                                               (gD_L**2+(1-yy[i,j])**2*gD_R**2)*(self.dbar[tar](xx[i,j],yy[i,j],ene,tar)+self.sbar(xx[i,j],yy[i,j],ene,tar)))
        return data
    
    def tot_cross_section(self, E_nu, f_nu, tar, x_low, x_top, y_low, y_top, eps):
        if f_nu > 0:
            d2s_xy_nu_CC = lambda x, y: 2*self.s_0(x,y,E_nu,tar)*(self.d[tar](x,y,E_nu,tar)+self.s(x,y,E_nu,tar)+ \
                                        (1-y)**2*(self.ubar[tar](x,y,E_nu,tar)+self.cbar(x,y,E_nu,tar)))
            tot_cs = dblquad(lambda y, x: d2s_xy_nu_CC(x,y), x_low, x_top, lambda x: y_low(x), lambda x: y_top(x), epsabs=eps)
        else:
            d2s_xy_anu_CC = lambda x, y: 2*self.s_0(x,y,E_nu,tar)*(self.dbar[tar](x,y,E_nu,tar)+self.sbar(x,y,E_nu,tar)+ \
                                         (1-y)**2*(self.u[tar](x,y,E_nu,tar)+self.c(x,y,E_nu,tar)))
            tot_cs = dblquad(lambda y, x: d2s_xy_anu_CC(x,y), x_low, x_top, lambda x: y_low(x), lambda x: y_top(x), epsabs=eps)
        return tot_cs[0]
    
    def plot_kinematic_boundaries(self, W_cut_list, E_nu, f_nu):
        
        x_low = np.empty(shape=len(W_cut_list))
        x_top = np.empty(shape=len(W_cut_list))
        y_low = np.empty(shape=len(W_cut_list),dtype=object)
        y_top = np.empty(shape=len(W_cut_list),dtype=object)
        x = np.empty(shape=len(W_cut_list),dtype=list)
        print(E_nu)
        for i, W_cut in enumerate(W_cut_list):
            x_low[i], x_top[i] = self.x_limits(W_cut, E_nu, f_nu)
            y_low[i], y_top[i] = self.y_limits(W_cut, E_nu, f_nu)
            print('x: ', x_low[i], x_top[i])
            print('y: ', y_low[i](x_low[i]), y_top[i](x_top[i]))
            
            x[i] = np.logspace(np.log10(x_low[i]),np.log10(x_top[i]),num=10000000)

        fig, ax = plt.subplots()

        M = (self.m_N[2212]+self.m_N[2112])*0.5
        y_minus = lambda x: (1-self.m_l[f_nu]**2/(2*E_nu**2)*(1+(E_nu)/(M*x))-np.sqrt((1-self.m_l[f_nu]**2/(2*M*x*E_nu))**2-self.m_l[f_nu]**2/E_nu**2))/(2*(1+(M*x)/(2*E_nu)))
        y_plus = lambda x: (1-self.m_l[f_nu]**2/(2*E_nu**2)*(1+(E_nu)/(M*x))+np.sqrt((1-self.m_l[f_nu]**2/(2*M*x*E_nu))**2-self.m_l[f_nu]**2/E_nu**2))/(2*(1+(M*x)/(2*E_nu)))
        x_minus = np.concatenate((np.logspace(np.log10(5.7e-8),np.log10(6e-8),num=35000000),np.logspace(np.log10(6e-8),1,10000000)))
        
        ax.plot(x_minus, y_plus(x_minus), label=r'$y^+$')
        ax.plot(x_minus, y_minus(x_minus), label=r'$y^-$')
        
        for i, W_cut in enumerate(W_cut_list):
            ax.plot(x[i], y_low[i](x[i]), label=r'$y^{cut}$, $M_h= $'+f'{W_cut}'+' GeV')
#            ax.plot(x[i], y_top[i](x[i]))
        ax.text(0.9,0.1,r"$\bf{E_\nu=}$"+f"{E_nu} GeV", verticalalignment='bottom', horizontalalignment='right',weight='bold',transform=ax.transAxes,fontsize=12)
        ax.set_xlabel('x Bjorken')
        ax.set_ylabel('y Bjorken')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim(1e-8,1)
        ax.set_ylim(1e-7,1)
        ax.minorticks_on()
        ax.set_axisbelow(True)
        ax.grid(which='major')
        ax.grid(which='minor',linestyle=':')
        ax.legend()
        
        plt.savefig(f'kinematic_boundaries_{E_nu}_GeV.pdf', dpi=1000)
        #plt.show()
    
    def plot_dis(self, xx, yy, dis):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

#        ax.plot_wireframe(xx,yy,dis[0].T)
        ax.plot_surface(xx,yy,dis[0],cmap=colormap.coolwarm,linewidth=0,antialiased=False)
        ax.set_xlabel(r'$x$', fontsize=14)
        ax.set_ylabel(r'$y$', fontsize=14)
        ax.set_title(r'$(\nu_\mu+\overline{\nu}_\mu)$ CC, NC effective volume / 8 clusters')
        #ax.set_xlim(1e2,1e5)
        ax.minorticks_on()
        ax.set_axisbelow(True)
        ax.grid(which='major')
        ax.grid(which='minor',linestyle=':')

        plt.savefig('dis.png', dpi=1000)
        plt.show()
    
    def dis_kinematics(self, x, y, E_nu, f_nu, tar, current):
        
        m_tar = self.m_N[tar]
        if current == 'CC':
            m_l   = self.m_l[f_nu]
        elif current == 'NC':
            m_l = 0.
        E_l   = (1.-y)*E_nu
        p_l = np.sqrt(E_l**2-m_l**2)
        
        cos_theta_l = (E_nu*E_l-0.5*(m_l**2+2*m_tar*E_nu*y*x))/(E_nu*p_l)
        sin_theta_l = np.sqrt(1.-cos_theta_l**2)
        phi_l       = 2*np.pi*np.random.uniform(size=1)[0]
        
        P_l = np.array([p_l*sin_theta_l*np.cos(phi_l),
                                           p_l*sin_theta_l*np.sin(phi_l),
                                           p_l*cos_theta_l])
        
        E_h = y*E_nu+m_tar
        P_h = np.array([-P_l[0],-P_l[1],E_nu-P_l[2]])
        
        return E_l, P_l.T, E_h, P_h.T
    
    def generate_xy(self, dis, xx, yy, n_events):
        
        cdf = np.cumsum(dis.ravel())
        cdf = cdf/cdf[-1]

        values = np.random.rand(n_events)

        value_bins = np.searchsorted(cdf, values)
        x_idx, y_idx = np.unravel_index(value_bins,np.shape(dis)[1:])
        
        return xx[x_idx,y_idx], yy[x_idx,y_idx]
    
    def density_PREM(self, r):
        a = R_E
        x = r/a
        
        d = np.piecewise(x, [r< 0, (r>=0*m) & (r<1221500*m),(1221500*m<=r) & (r<3480000*m),
                            (3480000*m<=r) & (r<5701000*m), (5701000*m<=r) & (r<5771000*m),
                            (5771000*m<=r) & (r<5971000*m), (5971000*m<=r) & (r<6151000*m),
                            (6151000*m<=r) & (r<6346600*m), (6346600*m<=r) & (r<6356000*m),
                            (6356000*m<=r) & (r<a), (a*m<=r) & (r<a*m+1366), r>a*m+1366],
                            [0, lambda x: (13.0885-8.8381*x*x), lambda x: (12.5815-x*(1.2638+x*(3.6426+x*5.5281))),
                            lambda x: (7.9565-x*(6.4761-x*(5.5283-x*3.0807))),
                            lambda x: (5.3197-1.4836*x), lambda x: (11.2494-8.0298*x),
                            lambda x: (7.1089-3.8045*x), lambda x: (2.691+0.6924*x), 2.9, 2.6, 1, 0])
        return d
    
    def depth_propability(self, r, E_nu, f_nu, x_low, x_top, y_low, y_top, eps):
        a = R_E
        x = r/a
        
        p = 0
        if r >= 0 and r < 3480000:
            d_core = np.piecewise(x, [(r>=0*m) & (r<1221500*m),(1221500*m<=r) & (r<3480000*m)],
                            [lambda x: (13.0885-8.8381*x*x), lambda x: (12.5815-x*(1.2638+x*(3.6426+x*5.5281)))])
            p += N_a*d_core*(self.n_p_core*self.tot_cross_section(E_nu, f_nu, 2212, x_low, x_top, y_low, y_top, eps)+ \
                             self.n_n_core*self.tot_cross_section(E_nu, f_nu, 2112, x_low, x_top, y_low, y_top, eps))
        elif r >= 3480000 and r < 6346600:
            d_mantle = np.piecewise(x, [(3480000*m<=r) & (r<5701000*m), (5701000*m<=r) & (r<5771000*m),
                            (5771000*m<=r) & (r<5971000*m), (5971000*m<=r) & (r<6151000*m),
                            (6151000*m<=r) & (r<6346600*m)],
                            [lambda x: (7.9565-x*(6.4761-x*(5.5283-x*3.0807))),
                            lambda x: (5.3197-1.4836*x), lambda x: (11.2494-8.0298*x),
                            lambda x: (7.1089-3.8045*x), lambda x: (2.691+0.6924*x)])
            p += N_a*d_mantle*(self.n_p_mantle*self.tot_cross_section(E_nu, f_nu, 2212, x_low, x_top, y_low, y_top, eps)+ \
                               self.n_n_mantle*self.tot_cross_section(E_nu, f_nu, 2112, x_low, x_top, y_low, y_top, eps))
        elif r >= 6346600 and r < a:
            d_crust = np.piecewise(x, [(6346600*m<=r) & (r<6356000*m),
                            (6356000*m<=r) & (r<a*m)],
                            [2.9, 2.6])
            p += N_a*d_crust*self.n_p_crust*(self.tot_cross_section(E_nu, f_nu, 2212, x_low, x_top, y_low, y_top, eps)+ \
                                             self.tot_cross_section(E_nu, f_nu, 2112, x_low, x_top, y_low, y_top, eps))
        else:
            d_water = np.piecewise(x, [(a*m<=r) & (r<a*m+1366), r>a*m+1366],
                            [1., 0.])
            p += N_a*d_water*(self.n_p_water*self.tot_cross_section(E_nu, f_nu, 2212, x_low, x_top, y_low, y_top, eps)+ \
                              self.n_n_water*self.tot_cross_section(E_nu, f_nu, 2112, x_low, x_top, y_low, y_top, eps))
        return p
    
    def init_point(self, r_f, n_f, r_d):
        x_f, y_f, z_f = r_f[0], r_f[1], r_f[2]
        nx_f, ny_f, nz_f = n_f[0], n_f[1], n_f[2]
        x_d, y_d, z_d = r_d[0], r_d[1], r_d[2]
        
        a = 1.
        b = 2*(nx_f*(x_f-x_d)+ny_f*(y_f-y_d)+nz_f*(z_f-z_d))
        c = x_d**2+y_d**2+z_d**2+x_f**2+y_f**2+z_f**2-2*(x_d*x_f+y_d*y_f+z_d*z_f)-R_E**2
        
        d = b**2 - 4*a*c

        u = (-b-d**0.5)/(2.*a)
        
        x_i, y_i, z_i = x_f+u*nx_f, y_f+u*ny_f, z_f+u*nz_f
        
        r_i = np.array([x_i, y_i, z_i])
        
        return r_i
    
    def column_depth_quad(self, r_f, n_f, r_d, eps):
        r_i = self.init_point(r_f, n_f, r_d)
        n = r_f - r_i
        l = np.sqrt(np.sum(n**2))
        R_i = r_i - r_d
        
        depth, err = quad(lambda t: self.density_PREM(np.sqrt(np.sum((R_i+n*t)**2)))*l, 0, 1, epsabs=eps)
        '''
        r = np.array([np.sqrt(np.sum((R_i+n*t)**2)) for t in np.linspace(0,1,10000000)])
        r_core   = len(r[r<3480*km])
        r_mantle = len(r[(r>=3480*km)&(r<6346.6*km)])
        r_crust  = len(r[r>=6346.6*km])
        r_total  = len(r)
        
        n_core   = r_core/r_total
        n_mantle = r_mantle/r_total
        n_crust  = r_crust/r_total
        
        p_core = n_core*depth
        p_mantle = n_mantle*depth
        p_crust = n_crust*depth
        
        x_low, x_top = self.x_limits(self.W_cut, 1000, 14)
        y_low, y_top = self.y_limits(self.W_cut, 1000, 14)
        print(p_core*(self.n_p_core*self.tot_cross_section(1000, 14, 2212, x_low, x_top, y_low, y_top, eps)+ \
                      self.n_n_core*self.tot_cross_section(1000, 14, 2112, x_low, x_top, y_low, y_top, eps))+ \
              p_mantle*(self.n_p_mantle*self.tot_cross_section(1000, 14, 2212, x_low, x_top, y_low, y_top, eps)+ \
                        self.n_n_mantle*self.tot_cross_section(1000, 14, 2112, x_low, x_top, y_low, y_top, eps))+ \
              p_crust*self.n_p_crust*(self.tot_cross_section(1000, 14, 2212, x_low, x_top, y_low, y_top, eps)+ \
                                      self.tot_cross_section(1000, 14, 2112, x_low, x_top, y_low, y_top, eps)))
        '''
        return depth, err
    
    def plot_PREM(self):
        r_f = np.array([0,0,1366])
        theta = 0
        phi = 0
        n_f = np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
        r_d = -np.array([0,0,R_E]) + r_f
        r_i = self.init_point(r_f, n_f, r_d)
        depth, err = self.column_depth_quad(r_f, n_f, r_d, 1e-4)
        
        u = np.linspace(0,2*np.pi,100)
        v = np.linspace(0,np.pi,100)

        x = R_E*np.outer(np.cos(u),np.sin(v))
        y = R_E*np.outer(np.sin(u),np.sin(v))
        z = R_E*np.outer(np.ones(np.size(u)),np.cos(v))
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.plot_surface(x+r_d[0], y+r_d[1], z+r_d[2],  rstride=4, cstride=4, color='y', linewidth=0, alpha=0.5)
        ax.scatter(r_f[0], r_f[1], r_f[2], color='b')
        ax.scatter(r_i[0], r_i[1], r_i[2], color='b')
        ax.set_xlabel(r'$x$, g/cm${}^2$', fontsize=14)
        ax.set_ylabel(r'density $\rho$, g/cm${}^3$', fontsize=14)
        ax.set_title(r'$(\nu_\mu+\overline{\nu}_\mu)$ CC, NC effective volume / 8 clusters')
        ax.minorticks_on()
        ax.set_axisbelow(True)
        ax.grid(which='major')
        ax.grid(which='minor',linestyle=':')
        ax.set_aspect('equal')
        
        n = r_f - r_i
        R_i = r_i - r_d
        r = np.array([np.sqrt(np.sum((R_i+n*t)**2)) for t in np.linspace(0,1,10000000)])
        
        fig, ax = plt.subplots()
        r = np.linspace(0,R_E+1366,1000000)
        ax.plot(r/1000, self.density_PREM(r), color='black')
        
        r_core   = r[r<3480*km]
        r_mantle = r[(r>=3480*km)&(r<6346.6*km)]
        r_crust  = r[(r>=6346.6*km)&(r<6368*km)]
        r_water  = r[r>=6368*km]
        
        plt.fill_between(
        x= r_core/1000, 
        y1= self.density_PREM(r_core), 
        color= "red",
        alpha= 0.2)
        
        plt.fill_between(
        x= r_mantle/1000, 
        y1= self.density_PREM(r_mantle), 
        color= "orange",
        alpha= 0.2)
        
        plt.fill_between(
        x= r_crust/1000, 
        y1= self.density_PREM(r_crust), 
        color= "brown",
        alpha= 0.2)
        
        plt.fill_between(
        x= r_water/1000, 
        y1= self.density_PREM(r_water), 
        color= "blue",
        alpha= 0.2)
        
        ax.set_xlim(0,None)
        ax.set_ylim(0,None)
        ax.set_xlabel(r'$r$, km', fontsize=14)
        ax.set_ylabel(r'$\rho$, g/cm${}^3$', fontsize=14)
#        ax.set_title(r'$(\nu_\mu+\overline{\nu}_\mu)$ CC, NC effective volume / 8 clusters')
        ax.minorticks_on()
        ax.set_axisbelow(True)
        ax.grid(which='major')
        ax.grid(which='minor',linestyle=':')
        
        ax2 = fig.add_axes([0.575, 0.55, 0.3, 0.3])
        ax2.plot(r[r>=6346.6*km]/1000, self.density_PREM(r[r>=6346.6*km]), color='black')
        ax2.set_xlim(6346.6,None)
        ax2.set_ylim(0,None)
        ax2.minorticks_on()
        ax2.set_axisbelow(True)
        ax2.grid(which='major')
        ax2.grid(which='minor',linestyle=':')
        
        ax2.fill_between(
        x= r_crust/1000, 
        y1= self.density_PREM(r_crust), 
        color= "brown",
        alpha= 0.2)
        
        ax2.fill_between(
        x= r_water/1000, 
        y1= self.density_PREM(r_water), 
        color= "blue",
        alpha= 0.2)

        plt.savefig('PREM.pdf', dpi=1000)
        plt.show()
    
    def plot_propability(self):
        eps = 1e-12
        f_nu = 14
        E_nu = np.logspace(np.log10(1e2),np.log10(1e8),1000)
#        E_nu = np.linspace(1e2,1e8,10)
        theta = np.linspace(90,180,1000)
        cos_theta = np.cos(np.radians(theta)+np.pi)
        phi = 0
        
        r_f = np.array([0,0,366])
        r_d = -np.array([0,0,R_E]) + np.array([0,0,1366])
        
        ee, zz = np.meshgrid(E_nu, theta)
        
        prob = np.empty(shape=(len(E_nu),len(cos_theta)))
        p_core   = np.empty(shape=len(cos_theta))
        p_mantle = np.empty(shape=len(cos_theta))
        p_crust  = np.empty(shape=len(cos_theta))
        p_water  = np.empty(shape=len(cos_theta))
        tot_cs_p = np.empty(shape=len(E_nu))
        tot_cs_n = np.empty(shape=len(E_nu))
        for i in range(np.shape(ee)[0]):
            print('ene: ', i)
            x_low, x_top = self.x_limits(self.W_cut, E_nu[i], f_nu)
            y_low, y_top = self.y_limits(self.W_cut, E_nu[i], f_nu)
            tot_cs_p[i] = self.tot_cross_section(E_nu[i], 14, 2212, x_low, x_top, y_low, y_top, eps)
            tot_cs_n[i] = self.tot_cross_section(E_nu[i], 14, 2112, x_low, x_top, y_low, y_top, eps)
        for j in range(np.shape(ee)[1]):
            print('cos: ', j)
            sin_theta = np.sqrt(1.-cos_theta[j]**2)
            n_f = np.array([sin_theta*np.cos(phi),sin_theta*np.sin(phi),cos_theta[j]])
            r_i = self.init_point(r_f, n_f, r_d)
            n = r_f - r_i
            l = np.sqrt(np.sum(n**2))
            R_i = r_i - r_d
            
            depth, err = quad(lambda t: self.density_PREM(np.sqrt(np.sum((R_i+n*t)**2)))*l, 0, 1, epsabs=eps)
            r = np.array([np.sqrt(np.sum((R_i+n*t)**2)) for t in np.linspace(0,1,1000000)])
        
            r_core   = len(r[r<3480*km])
            r_mantle = len(r[(r>=3480*km)&(r<6346.6*km)])
            r_crust  = len(r[(r>=6346.6*km)&(r<6368*km)])
            r_water  = len(r[r>=6368*km])
            r_total  = len(r)
            
            n_core   = r_core/r_total
            n_mantle = r_mantle/r_total
            n_crust  = r_crust/r_total
            n_water  = r_water/r_total
            
            p_core[j]   = n_core*depth
            p_mantle[j] = n_mantle*depth
            p_crust[j]  = n_crust*depth
            p_water[j]  = n_water*depth
        
        p_core   = np.repeat(p_core[:,None],len(theta),axis=1)
        p_mantle = np.repeat(p_mantle[:,None],len(theta),axis=1)
        p_crust  = np.repeat(p_crust[:,None],len(theta),axis=1)
        p_water  = np.repeat(p_water[:,None],len(theta),axis=1)
        tot_cs_p = np.repeat(tot_cs_p[None,:],len(E_nu),axis=0)
        tot_cs_n = np.repeat(tot_cs_n[None,:],len(E_nu),axis=0)
        '''
        flux_data = pd.read_csv('Av_numu_H3a_KM_E2.dat' ,header=None, sep ='\t')
        energy    = np.array(flux_data[0])
        flux      = np.array(flux_data[1])/energy**2
        flux_interp = lambda ene: np.interp(ene, energy, flux)
        
        eta_nu = lambda y, E: flux_interp(E/(1.-y))/(flux_interp(E)*(1.-y))
        D_nu = lambda y, E: N_a*((self.n_p_core*self.tot_cross_section(E/(1.-y), 14, 2212, x_low, x_top, y_low, y_top, eps) + self.n_n_core*self.tot_cross_section(E/(1.-y), 14, 2112, x_low, x_top, y_low, y_top, eps)) - \
                                 (self.n_p_core*self.tot_cross_section(E, 14, 2212, x_low, x_top, y_low, y_top, eps) + self.n_n_core*self.tot_cross_section(E, 14, 2112, x_low, x_top, y_low, y_top, eps)))
        '''
        depth_prob = N_a*100*(p_core*(self.n_p_core*tot_cs_p+self.n_n_core*tot_cs_n)+ \
                              p_mantle*(self.n_p_mantle*tot_cs_p+self.n_n_mantle*tot_cs_n)+ \
                              p_crust*self.n_p_crust*(tot_cs_p+tot_cs_n) + \
                              p_water*(self.n_p_water*tot_cs_p+self.n_n_water*tot_cs_n))
        prob = np.exp(-depth_prob)

        fig, ax = plt.subplots()
        
        im = ax.pcolormesh(ee, zz, prob, cmap='jet', shading='gouraud')
#        ax.set_title(r'$\nu_\mu$, CC', fontsize=14)
        ax.set_title('Transmission probability at depth = 1000 m', fontsize=14)
        ax.set_xlabel(r'$E_\nu$, GeV', fontsize=14)
        ax.set_ylabel(r'Zenith angle $\theta$, deg', fontsize=14)
        ax.set_xscale('log')
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Transmission propability', fontsize=14)
        
        plt.savefig('NuProp.pdf', dpi=1000)
        plt.show()
    
    @report_timing
    def make_event(self, event):
        #self.plot_PREM()
        #self.plot_kinematic_boundaries([1.2,1.4,1.6,1.8,2.],self.energy_GeV,14)
        #self.plot_propability()
        
        self.particles_init = gParticles('primary_init', to_propagate=False, gen_cher=False)
        self.particles_prop = gParticles('primary_prop', gen_cher=False)
        
        P_nu = self.P_nu[self.n_event]
        target = self.target[self.n_event]
        position_m = self.position_m[self.n_event]
        event.EventHeader.event_weight = self.weight[self.n_event]
        '''
        rng = np.random.default_rng()
        
        cos_theta_nu = rng.uniform(low=self.cos_theta_range[0],high=self.cos_theta_range[1],size=1)
        sin_theta_nu = np.sqrt(1.-cos_theta_nu**2)
        phi_nu       = rng.uniform(low=self.phi_range[0],high=self.phi_range[1],size=1)
        P_nu = np.array([self.energy_GeV*sin_theta_nu*np.cos(phi_nu),
                         self.energy_GeV*sin_theta_nu*np.sin(phi_nu),
                         self.energy_GeV*cos_theta_nu]).T
        
        if self.random_position:
            position_m, weight = self.set_random_position(1,self.random_volume)
            event.EventHeader.event_weight = weight
        else:
            position_m = np.array(self.position_m)
        
        gamma_1 = rng.random(size=1)
        
        if position_m[2] < 0: p_target = np.cumsum([self.n_p_crust,self.n_n_crust])
        else: p_target = np.cumsum([self.n_p_water,self.n_n_water])
        if gamma_1 < p_target[0]: target = 2212
        else: target = 2112
        target = self.target
        '''
        '''
        if self.cross_section_mode == 'calculate':
            
            x_low, x_top = self.x_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            y_low, y_top = self.y_limits(self.W_cut, self.energy_GeV, self.flavour_nu)
            
            x_min = np.min(x_low)
            x_max = np.max(x_top)
            y_min = np.min(y_low(x_min))
            y_max = np.max(y_top(x_max))
            
            xs = np.linspace(x_min, x_max, num=self.x_bins)
            ys = np.linspace(y_min, y_max, num=self.y_bins)
            
            xx, yy = np.meshgrid(xs, ys)
            
            if self.current_mode == 'CC':
                if self.flavour_nu > 0:
                    dis = self.d2s_xy_nu_CC(xx, yy, [self.energy_GeV], target, y_low, y_top)
                else:
                    dis = self.d2s_xy_anu_CC(xx, yy, [self.energy_GeV], target, y_low, y_top)
            if self.save_data:
                np.savez(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{target}', dis, xx, yy)
        elif self.cross_section_mode == 'data':
            data = np.load(f'data_{self.flavour_nu}_{self.current_mode}_{self.energy_GeV}GeV_tar_{target}.npz')
            dis, xx, yy = data['arr_0'], data['arr_1'], data['arr_2']
        
        self.plot_PREM()
        self.plot_kinematic_boundaries(self.W_cut, self.energy_GeV, self.flavour_nu)
        self.plot_dis(xx, yy, dis)
        
        x, y = self.generate_xy(dis, self.xx, self.yy)
        
        fig, ax = plt.subplots(2)

        hist_y, bin_edges_y = np.histogram(y,bins=100,density=True)

        ax[0].stairs(hist_y, bin_edges_y)
        ax[0].minorticks_on()
        ax[0].set_axisbelow(True)
        ax[0].grid(which='major')
        ax[0].grid(which='minor',linestyle=':')
        ax[0].set_xlabel('y')

        hist_x, bin_edges_x = np.histogram(x,bins=100,density=True)

        ax[1].stairs(hist_x, bin_edges_x)
        ax[1].minorticks_on()
        ax[1].set_axisbelow(True)
        ax[1].grid(which='major')
        ax[1].grid(which='minor',linestyle=':')
        ax[1].set_xlabel('x')
        
        plt.show()
        '''
        x = self.x[self.n_event]
        y = self.y[self.n_event]
        '''
        fig, ax = plt.subplots(2)

        hist_y, bin_edges_y = np.histogram(self.y,bins=100,density=True)

        ax[0].stairs(hist_y, bin_edges_y)
        ax[0].minorticks_on()
        ax[0].set_axisbelow(True)
        ax[0].grid(which='major')
        ax[0].grid(which='minor',linestyle=':')
        ax[0].set_xlabel('y')

        hist_x, bin_edges_x = np.histogram(self.x,bins=100,density=True)

        ax[1].stairs(hist_x, bin_edges_x)
        ax[1].minorticks_on()
        ax[1].set_axisbelow(True)
        ax[1].grid(which='major')
        ax[1].grid(which='minor',linestyle=':')
        ax[1].set_xlabel('x')
        
        plt.show()
        '''
        E_l, P_l, E_h, P_h = self.dis_kinematics(x, y, self.energy_GeV, self.flavour_nu, target, self.current_mode)
        
        self.particles_init.from_custom_array([0, self.flavour_nu, position_m, 0., P_nu, self.energy_GeV], gParticles.data_type.names)
        self.particles_init.from_custom_array([0, target, position_m, 0., np.zeros(3), self.m_N[target]], gParticles.data_type.names)
        
        if self.current_mode == 'CC':
            self.particles_prop.from_custom_array([0, self.f_l[self.flavour_nu], position_m, 0., P_l, E_l])
            if target == 2212:
                if self.flavour_nu > 0:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, 211, 2212)
                    self.particles_prop.from_custom_array([0, 211, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2212, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
                else:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, 111, 2112)
                    self.particles_prop.from_custom_array([0, 111, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2112, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
            elif target == 2112:
                if self.flavour_nu > 0:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, 211, 2112)
                    self.particles_prop.from_custom_array([0, 211, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2112, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
                else:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, -211, 2112)
                    self.particles_prop.from_custom_array([0, -211, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2112, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
        elif self.current_mode == 'NC':
            self.particles_prop.from_custom_array(0, 0, self.flavour_nu, position_m, 0., P_l, E_l, 0)
            if target == 2212:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, 211, 2112)
                    self.particles_prop.from_custom_array([0, 211, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2112, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
            elif target == 2112:
                    momentum_pi, tot_energy_pi, momentum_p, tot_energy_p = resonance_decay(P_h, E_h, 111, 2112)
                    self.particles_prop.from_custom_array([0, 111, position_m, 0., momentum_pi, tot_energy_pi], gParticles.data_type.names)
                    self.particles_prop.from_custom_array([0, 2112, position_m, 0., momentum_p, tot_energy_p], gParticles.data_type.names)
            
        event.particles = self.particles_init
        event.particles = self.particles_prop
        
        self.n_event += 1