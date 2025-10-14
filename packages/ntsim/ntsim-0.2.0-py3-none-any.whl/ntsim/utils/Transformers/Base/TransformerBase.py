import abc
from argparse import Namespace

class TransformerBase(metaclass=abc.ABCMeta):
    def __init__(self,name):
        self.name = name
        self.module_type = 'transformer'
        import logging
        self.log = logging.getLogger(name)
        self.log.info("initialized transformer")

    @abc.abstractmethod
    def configure(self,opts: Namespace) -> bool:
        pass

    @abc.abstractmethod
    def transform(self,variable):
        pass