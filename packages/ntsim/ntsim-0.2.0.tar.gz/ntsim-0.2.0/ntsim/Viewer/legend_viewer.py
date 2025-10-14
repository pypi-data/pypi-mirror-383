import numpy as np
from pyqtgraph.opengl import GLGraphicsItem

from particle import Particle
import ntsim.utils.pdg_colors as dict_colors

from collections import Counter

from webcolors import rgb_to_name

class GLPainterItem(GLGraphicsItem.GLGraphicsItem):
    def __init__(self, **kwds):
        super().__init__()
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)

    def configure(self, widget, particle_id, cascades):
        self.widget = widget
        self.particle_id = particle_id
        self.cascade_id = cascades
#        self.info = {}

    def particle_table(self, pdgid, amount_of_particles, colour):
        return [Particle.from_pdgid(pdgid), pdgid, amount_of_particles, rgb_to_name(colour)]

    def particle_types(self, particles):
        tracks_table = np.empty([len(particles)+1, 4], dtype = object) #The second index means number of particle parameters
        #In this edition, this are Particle, Pdgid, Amount of tracks / cascades and the Colour of the corresponding track
        tracks_table[0] = ['Particle', 'PDGID', 'Amount', 'Colour']
        counter = 1
        for uid in particles.most_common():
            if uid[0] in dict_colors.pdg_colors:
                tracks_table[counter] = self.particle_table(uid[0], uid[1], dict_colors.pdg_colors[uid[0]])
            else:
                if uid[0]>1000000000:
                    # this a nucleus or an ion
                    # get last digit: if not zero --> this is an excited ion
                    I = np.int64(repr(uid[0])[-1])
                    prtcl = uid[0] - I
                    tracks_table[counter] = self.particle_table(prtcl, uid[1], dict_colors.pdg_colors_others)
                else:
                    tracks_table[counter] = self.particle_table(uid[0], uid[1], dict_colors.pdg_colors_others)
            counter += 1
        return tracks_table

    def state_info(self, key = 'Tracks'):
        if key == 'Tracks':
            track_types = Counter([track[0] for track in self.particle_id.values()])
            return self.particle_types(track_types)
        elif key == 'Cascades':
            cascade_types = Counter([track for track in self.cascade_id[0]['Primary']['pdgid']]) #fixme (was 'g4_cascade_starters')
            return self.particle_types(cascade_types)

    
    def paint(self):
        particles = []
        self.setupGLState()
        self.painter = QtGui.QPainter(self.view())
        particle_types = Counter([track[0] for track in self.particle_id.values()])
        cascade_types = Counter([track for track in self.cascade_id['g4_cascade_starters']['pdgid']])
        #tracks legend>>>
        indent = 30
        tab = 0
#        print('double draw: ')
        self.painter.setPen(QtCore.Qt.GlobalColor.white)
        self.painter.drawText(tab, 15, 'Tracks:')
        for particle in particle_types.most_common():
            if particle[0] in dict_colors.pdg_colors:
                self.draw(self.painter, particle[0], particle[1], dict_colors.pdg_colors[particle[0]], tab, indent)
                indent += 15
        #cascades legend>>>
        indent = 30
        tab = 120
        self.painter.setPen(QtCore.Qt.GlobalColor.white)
        self.painter.drawText(tab, 15, 'Cascades:')
        for cascade in cascade_types.most_common():
            if cascade[0] in dict_colors.pdg_colors:
                self.draw(self.painter, cascade[0], cascade[1], dict_colors.pdg_colors[cascade[0]], tab, indent)
            else:
                self.draw(self.painter, cascade[0], cascade[1], dict_colors.pdg_colors_others, tab, indent)
            indent += 15
        #other tracks legend>>>
        tab = QtCore.Qt.AlignmentFlag.AlignRight
        self.painter.setPen(QtCore.Qt.GlobalColor.white)
        lines = []
        for particle in particle_types.most_common():
            if particle[0] not in dict_colors.pdg_colors:
                lines.append(f"{particle[0]}: {particle[1]}")
        self.painter.setPen(QtGui.QColor(*dict_colors.pdg_colors_others))
        self.painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        info = '\n'.join(lines)
        info = 'Other tracks: \n' + info
        rect = self.view().rect()
        af = QtCore.Qt.AlignmentFlag
        self.painter.drawText(self.view().rect(), af.AlignTop | af.AlignRight, info)
        self.painter.end()

    
    def setVisible_legend(self, value='False'):
#        self.setupGLState()
#        painter = QtGui.QPainter(self.view())
        if value == True:
            self.painter.begin(self.view())
            particle_types = Counter([track[0] for track in self.particle_id.values()])
            cascade_types = Counter([track for track in self.cascade_id['g4_cascade_starters']['pdgid']])
            indent = 30
            tab = 240
            lines = []
            for particle in particle_types.most_common():
                if particle[0] not in dict_colors.pdg_colors:
                    lines.append(f"{particle[0]}: {particle[1]}")
#                    self.draw(self.painter, particle[0], particle[1], dict_colors.pdg_colors_others, tab, indent)
#                    indent += 15
            self.painter.setPen(QtGui.QColor(*dict_colors.pdg_colors_others))
            self.painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
            self.info = "\n".join(lines)
            rect = self.view().rect()
            af = QtCore.Qt.AlignmentFlag
#            self.painter.drawText(self.view().rect(), af.AlignTop | af.AlignRight, self.info)
            self.painter.drawText(tab, indent, 'HI!')
            self.viewTransform()
            self.painter.end()
        elif value == False:
            self.clean_view()
    

    def draw(self, painter, particle, number_of_particles, color_particle, tab, indent):
        painter.setPen(QtGui.QColor(*color_particle))
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)

        add_info = ""
        if particle>1000000000:
            # this a nucleus or an ion
            # get last digit: if not zero --> this is an excited ion
            I = int(repr(particle)[-1])
            if I:
                particle = particle - I
                add_info = "excited"
        self.info[particle] = f"{Particle.from_pdgid(particle)} : {number_of_particles}"+add_info
        if type(tab) != int:
            rect = self.view().rect()
            painter.drawText(rect, tab, self.info[particle])
        else:
            painter.drawText(tab, indent, self.info[particle])
    

    def setVisible_legend(self, value = False):
        pass
#        if value == False:
#            self.clean_view()

    def clean_view(self):
        pass
#        self.info = {}

    def display_frame(self):
        pass

    def display_static(self):
        pass
