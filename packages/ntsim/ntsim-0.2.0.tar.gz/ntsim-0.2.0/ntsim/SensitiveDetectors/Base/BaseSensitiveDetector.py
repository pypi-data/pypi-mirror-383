from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from ntsim.Propagators.RayTracers.rt_utils import detector_response
from ntsim.Telescopes.Base.BoundingBoxNode import BoundingBoxNode
from ntsim.Base.BaseConfig import BaseConfig
import numpy as np
from dataclasses import dataclass
from numba import typed, types
# Define the function type
effect_type = types.float64(types.float64[:], types.float64[:]).as_type()

class BaseSensitiveDetector(BaseConfig):
    instance_count = 0  # Class variable to keep track of instances
    def __init__(self, uid, position, shape, parent=None):
        BaseSensitiveDetector.instance_count+=1
        self.uid              = uid
#        self._effects         = []
        self._effects         = typed.List.empty_list(effect_type)        # list of effects
        self._effects_options = []        # array of options as np.array for each effect
        self._effects_names   = []        # array of effect's names
        self._position        = position  # The position of the detector in 3D space
        self._shape           = shape     # The shape of the detector
        self._parent          = parent    # parent box

    @classmethod
    def print_instance_count(cls):
        cls.logger.info(f"initialized {cls.instance_count} instances")

    def add_effect(self, effect_function, effect_options, effect_name):
        if not callable(effect_function):
            raise ValueError("Effect function must be callable.")

        if not isinstance(effect_options, np.ndarray):
            raise ValueError("Effect options must be a numpy array.")

        if not isinstance(effect_name, str):
            raise ValueError("Effect name must be a string.")

        self._effects.append(effect_function)
        self._effects_options.append(effect_options)
        self._effects_names.append(effect_name)

    @property
    def effects(self) -> typed.List:
        return self._effects

    @effects.setter
    def effects(self, value: typed.List):
        self._effects = value

    @property
    def effects_options(self) -> typed.List:
        return self._effects_options

    @effects_options.setter
    def effects_options(self, value: typed.List):
        self._effects_options = value

    @property
    def effects_names(self) -> typed.List:
        return self._effects_names

    @effects_names.setter
    def effects_names(self, value: typed.List):
        self._effects_names = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    @property
    def parent(self) -> BoundingBoxNode:
        return self._parent

    @parent.setter
    def parent(self, value: BoundingBoxNode):
        self._parent = value

    @abstractmethod
    def line_segment_intersection(self, a: Any, b: Any) -> Any:
        """
        Calculate the intersection of a line segment with the detector.

        Parameters:
        a,b: 3d arrays for begining and end of the line segment

        Returns:
        The intersection information.
        """
        pass

    def response(self,wavelength,intersection):
        return detector_response(wavelength,intersection,self.effects,self.effects_options,self.effects_names)
