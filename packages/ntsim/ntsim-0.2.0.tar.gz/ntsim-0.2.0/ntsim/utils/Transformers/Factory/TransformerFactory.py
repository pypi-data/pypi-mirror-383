from ntsim.Base.BaseFactory import BaseFactory
from ntsim.utils.Transformers.Base.TransformerBase import TransformerBase

class TransformerFactory(BaseFactory):
    def __init__(self):
        super().__init__(base_package='ntsim.utils.Transformers', base_class=TransformerBase)
    
    def configure(self, opts):
        super().configure(opts, 'transformer_name')
