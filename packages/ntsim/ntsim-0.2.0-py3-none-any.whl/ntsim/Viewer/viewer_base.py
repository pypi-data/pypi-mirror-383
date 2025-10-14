import abc

class viewerbase(metaclass=abc.ABCMeta):
    def __init__(self,frames=[]):
        """
        ctor with widget and data to display
        """
        self.docks   = {}
        self.widgets = {}
        self.data    = {}
        self.frames  = frames

    def set_docks(self,docks):
        self.docks = docks

    def set_widgets(self,widgets):
        self.widgets = widgets

    def set_data(self,data):
        self.data = data

    def set_frames(self,frames):
        self.frames = frames

    @abc.abstractmethod
    def display_static(self):
        """
        display data time integrated
        """

    @abc.abstractmethod
    def display_frame(self,frame):
        """
        display given frame
        """

    @abc.abstractmethod
    def configure(self,opts):
        """
        configure the viewer
        """
