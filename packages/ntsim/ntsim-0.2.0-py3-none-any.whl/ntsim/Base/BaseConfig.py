from abc import ABC, abstractmethod
import logging

class _logger_descriptor:
    """A class that will provide correct loggers for this given class"""
    def __get__(self, instance, owner):
        return logging.getLogger('NTSim.'+owner.__name__)
        
class BaseConfig(ABC):
    arg_dict = {}    
    logger = _logger_descriptor()
    
    @classmethod
    def add_args(cls, parser):
        for arg, meta in cls.arg_dict.items():
            unique_name = f"{cls.__name__}.{arg}"
            arg_options = {}
            if 'type' in meta:
                arg_options['type'] = meta['type']
            if 'default' in meta:
                arg_options['default'] = meta['default']
            if 'help' in meta:
                arg_options['help'] = meta['help']
            if 'action' in meta:
                arg_options['action'] = meta['action']
            if 'nargs' in meta:
                arg_options['nargs'] = meta['nargs']
            if 'choices' in meta:
                arg_options['choices'] = meta['choices']
            #print(unique_name,arg_options)
            parser.add_argument(f"--{unique_name}", **arg_options)
    def __post_configure__(self):
        "A hook to be called after the configure()"
        pass
        
    def configure(self, opts):
        # print(f'-- configuring {self.__name__} --')
        if isinstance(self, type):
            module_name = self.__name__
        else:
            module_name = self.__class__.__name__
        for arg in self.arg_dict.keys():
            unique_name = f"{module_name}.{arg}"
            if hasattr(opts, unique_name):
                value = getattr(opts, unique_name)
                setattr(self, arg, value)
                self.arg_dict[arg]['value'] = value
        if not isinstance(self, type):
            #call the post_init hook
            self.__post_configure__()

    @classmethod
    def configure_class(cls, opts):
        #just call the other method, although it's rather ugly...
        cls.configure(cls, opts)