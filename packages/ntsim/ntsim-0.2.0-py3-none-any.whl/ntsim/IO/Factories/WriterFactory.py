from ntsim.Base.BaseFactory import BaseFactory
from ntsim.IO.Base.WriterBase import WriterBase

class WriterFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.IO', base_class=WriterBase)
    
    def configure(self, opts):
        super().configure(opts, 'writer_name')
