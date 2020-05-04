#-----------------------------------------------------------------------
# This file is part of Nazca.
#
# Nazca is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# Nazca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Nazca.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------
# @author: Ronald Broeke (c) 2016-2017
# @email: ronald.broeke@brightphotonics.eu
#
"""Multi layer solver interface. Needs external c file."""

from sys import exit
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .simglobal import sim
from . import cfg


slabpath = './nazca/'

class Slabsolver():
    """Multi-layer slabmode solver."""

    def __init__(self, wl=None, pol=None, mode=0, name='', layers=None, points=100, view='topview'):
        """
        :wl: wavelength
        :pol: polarization
        :mode: optical mode
        :name: name of the solver
        :layers: list of layer tuples (material, width)
        :points: point to calculate for a mode field
        :view: 'topview' or 'sideview'
        """
        self.view = view
        if view not in ['topview', 'sideview']:
            exit('View not existing: '+view+'\n')
        self.set(wl, pol, mode, layers, points)
        self.name = name
        self.plotNum = 0
        if name is None:
            self.name = 'multi-layer-solver'
        else:
            self.name = name


    def set(self, wl=None, pol=None, mode=None, layers=None, points=None):
        if wl is not None: self.wl = wl
        else: self.wl=sim.wl

        if pol is not None:
            if pol == 'TE': self.pol = 0
            elif pol == 'TM': self.pol = 1
            else: self.pol = pol
        else: self.pol=sim.pol

        if mode is not None:
            self.mode = mode
        if points is not None:
            self.points = points
        if layers is not None:
          self.layers = layers
        if self.layers is not None:
            self.Mat, self.D = zip(*self.layers)
        else:
            self.Mat, self.D = None, None

        return self


    def getField(self):
        if self.Mat is None:
            exit('No materials defines. Can not calculate field.')
        N = [m.Neff(wl=self.wl, pol=self.pol) for m in self.Mat]
        if self.pol==0: polstr ='TE'
        elif self.pol==1: polstr ='TM'
        #create slabin.dat
        slabin = """
        Wavelength (um) = {}
        Polarisation = {}
        Mode order = {}
        Number of layers = {}
        Refractive indices = {}
        Thicknesses (um) = {}
        Number of plot intervals = {}
        """.format(self.wl, polstr, self.mode, len(N),
                   ' '.join(map(str,N)), ' '.join(map(str,self.D)), self.points)

        with open('slabin.dat', 'w') as text_file:
            text_file.write(slabin)


        #create slabout.dat, read data and use subprocess to get retrun value
        proc = subprocess.Popen(slabpath+"slab", stdout=subprocess.PIPE, shell=True)
        stdout, err = proc.communicate()
        a = (stdout.decode('UTF-8'))
        a = a.split('=')[-1]
        a = a.rstrip('\n')
        try:
            self.__Neff = float(a)
        except:
            nd.cfg.print_except("bare-except:")
            exit('(slab): No mode in layer \'{}\': {}'.format(self.name, a))

        self.__field = pd.read_csv('slabout.dat', delimiter=' ', names=['x','E'])
        try: len(self.__field)
        except:
            nd.cfg.print_except("bare-except:")
            print ('It seems there is no field returned by Slabsolver '+name)
        return self.__field, self.__Neff


    def plot(self, title=None, rotate=False, **kwargs):
        cfg.formatplot()

        if title is None:
            title = self.name

        field, Neff = self.getField()
        x = kwargs.pop('x', 'x')
        y = kwargs.pop('y', 'E')
        xlabel = 'x [um]'
        ylabel = 'E [field normalized]'
        clip_on = kwargs.get('clip_on', False)
        if rotate==True:
            x, y = y, x
            ylabel, xlabel = 'y [um]', ylabel
        ax = kwargs.pop('ax', None)
        if ax is None:
            fig, ax = plt.subplots(figsize=cfg.modeplotsize)

        #ax = self.ax
        if self.pol==0: col = 'b'
        else: col = 'g'
        linestyles = ['-', '-', '-', '-']*8
        ls = linestyles[self.mode]

        Dc = np.cumsum(self.D)
        Dc = np.insert(Dc,0,[0])

        if self.plotNum >= 0:
            ax.set_title(title)

            if rotate==False:
                ax.set_xlim([Dc[0], Dc[-1]])
            else:
                ax.set_ylim([Dc[0], Dc[-1]])
            for i,d in enumerate(Dc[:-1]):
                if rotate==False:
                    p = ax.axvspan(Dc[i], Dc[i+1], facecolor='m', alpha=0.01+0.05*(self.Mat[i].Neff()-1))
                else:
                    p = ax.axhspan(Dc[i], Dc[i+1], facecolor='m', alpha=0.01+0.05*(self.Mat[i].Neff()-1))
            [ax.spines[key].set_linewidth(2.0) for key in ax.spines.keys()]

        field.plot(x=x, y=y, ls=ls, color=col, clip_on=clip_on, ax=ax, **kwargs)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.tight_layout()

        self.plotNum += 1
        return ax


    def __str__(self):
        out = 'Slab-solver settings:'
        out += '\n- slab name                            :\''+ self.name +'\''
        out += '\n- type                                 : MLS (multi-layer-solver)'
        out += '\n- view                                 : ' + self.view
        out += '\n- wavelength                 - wl [um] : ' + str(self.wl)
        out += '\n- polarization               - pol     : ' + str(self.pol)
        out += '\n- materials                  - M       : ' + ', '.join([m.name for m in self.Mat])
        out += '\n- layer thickeness           - D [um]  : ' + ', '.join(map(str,self.D))
        out += '\n- refractive indices         - N       : ' + ', '.join(map(str,[m.Neff() for m in self.Mat]))
        out += '\n- number of points for Field - points  : ' + str(self.points)
        out += '\n'
        return out


    def Neff(self, **kwargs):
        self.wl = kwargs.get('wl', sim.wl)
        self.pol = kwargs.get('pol', sim.pol)
        kwargs['wl'] = self.wl
        kwargs['pol'] = self.pol
        a, b = self.getField()
        return b


    @property
    def field(self):
        self.getField()
        return self.__field


