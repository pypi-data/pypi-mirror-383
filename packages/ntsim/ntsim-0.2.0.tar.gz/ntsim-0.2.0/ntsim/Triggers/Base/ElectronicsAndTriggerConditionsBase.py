import numpy as np
import abc

class ElectronicsAndTriggerConditionsBase():
    
    def __init__(self, label: str):
        self.label = label
        self.functions = []
        #always call to initialize the functions
        self.set_functions()
    
    def add_function(self, function):
        self.functions.append(function)
    
    @abc.abstractmethod
    def set_functions(self) -> None:
        pass

    def apply_functions(self, hits): # called from object of electronics or trigger
        fhits = hits
        for f in self.functions:
            fhits = f(fhits)
            if len(fhits)==0:
                break
        return fhits
