import numpy as np
from inspect import Signature, Parameter
from typing import ClassVar, TypeVar, Type
from ntsim.utils import io_utils
from functools import wraps

from dataclasses import dataclass, Field, _MISSING_TYPE

from typing import Set, List, Optional
from ntsim.Base.BaseConfig import BaseConfig

class FieldSelector:
    """A descriptor class to select a subset of fields from an input.
    Usage: 
    
    ```python
    @dataclass
    class A:
        #data fields
        x: np.float16 = 0.
        n: np.int16 = 1
        #add descriptor
        data_save = FieldSelector()

    a = A() #make class instance
    
    a.data_save 
    #returns: {'n', 'x'}
    
    A.arg_dict
    #returns:
    #{'data_save': {'type': str,
    #  'nargs': '*',
    #   'choices': ['x', 'n'],
    #  'default': ['x', 'n']}}
    ```
    """
    def __init__(self, fields: Optional[Set[str]|List[str]] = None):
        self._available_fields = fields
        self._selected_fields: Set[str] = set()

    def __set_name__(self, cls, descriptor_name):
        if self._available_fields is None:
            self._available_fields = set(cls.__annotations__)

        self._selected_fields = self._available_fields.copy()

        # Register in the owner's argdict
        cls.arg_dict = dict(getattr(cls, 'arg_dict', {}))
        cls.arg_dict[descriptor_name] = {
            'type': str,
            'nargs': '*',
            'choices': list(self._available_fields),
            'default': list(self._available_fields)
        }
    def __get__(self, obj, objtype=None):
        return self._selected_fields
    def __set__(self, obj, value):
        self._selected_fields = set(value)

    def add_to_class(self, owner, name:str):
        "add this descriptor to a class 'owner' with name='name'"
        #add descriptor to the class
        setattr(owner, name, self)
        self.__set_name__(owner, name)
        
T = TypeVar('T', bound='StructData')

#some useful methods
def _make_properties_for_all_fields(cls, names):
    """Initialize a property for each field"""
    def make_property(field_name, docstring=None):
        return property(
            lambda self: self._get_field(name=field_name),
            lambda self, value: self._set_field(name=field_name, value=value),
            doc=docstring
        )
    for name in names:
        setattr(cls, name, make_property(name))
        
def _expand_function_signature(function, names, **arg_defaults):
    """Take a signature from the given function, and expand the variadic keyword arguments,
    set them to individual arguments (arg_names) and enforce the defaults (arg_defaults).

    Parameters
    ----------
    function: callable
        The function for which we will enforce a new signature
    names: iterable[str]
        list of the argument names
    arg_defaults: dict[str, value]
        default values to some (or all) the arguments
    Returns
    -------
        the wrapped function
    """
    
    S = Signature.from_callable(function)
    #select non-variadic aprameters
    non_var_params = [param for param in S.parameters.values() if param.kind!=Parameter.VAR_KEYWORD]
    new_params = [Parameter(name, 
                            kind=Parameter.KEYWORD_ONLY, 
                            default=arg_defaults.get(name, Parameter.empty)
                           ) 
                  for name in names
                  #remove the parameters if they are already present in the c-tor
                  if name not in S.parameters 
                 ]
    S = Signature(non_var_params+new_params)

    @wraps(function)
    def wrapped_function(self, *args, **kwargs):
        bound_params = S.bind(self, *args, **kwargs)
        bound_params.apply_defaults()
        #call the inner function
        function(**bound_params.arguments)
        
    wrapped_function.__signature__ = S
    return wrapped_function

def _get_default_values(cls, names):
    "Get the default values of the arguments with given names"
    arg_defaults = {name: getattr(cls, name) for name in names if hasattr(cls, name)}
    for name, val in arg_defaults.items():
        if isinstance(val, Field):
            #this is workaround for Fields
            arg_defaults[name]=val.default
    #delete the missing defaults
    arg_defaults = {name:val 
                    for name,val in arg_defaults.items() 
                    if not isinstance(val, _MISSING_TYPE)
                   }
    return arg_defaults




class StructData(BaseConfig):
    """A container class to provide access to the structdata arrays inside it.
    It must be first initialized with a dtype, for example::
        My_Particle_Data = StructData[[('position', 'f8',3), ('energy', 'f8')]]
    """
    _dtype: ClassVar[np.dtype]
    
    def __init__(self, size, **kwargs):
        self._data = np.empty(size, dtype=self._dtype)
        self.metadata = {}
        # set the field values
        for name, value in kwargs.items():
            setattr(self, name, value)
    
    def __init_subclass__(cls, **kwargs):
        """Initialize subclass and generate structured dtype from annotations.
        Automatically generates `_dtype` class attribute based on field type annotations.
        """
        super().__init_subclass__(**kwargs)
        #define the important variables
        if not hasattr(cls, '_dtype'):
            cls._dtype = io_utils.get_dtype(cls.__annotations__)
        cls.field_names = cls._dtype.names
        # fill in the signature
        args_default = _get_default_values(cls, cls.field_names)
        cls.__init__ = _expand_function_signature(cls.__init__, 
                                                  cls.field_names, 
                                                  **args_default)
        # fill in the class properties to acccess fields
        _make_properties_for_all_fields(cls, cls.field_names)
        # add data selector
        FieldSelector().add_to_class(cls, name='data_save')

    def __len__(self):
        return len(self._data)
    def __repr__(self):
        return f"{self.__class__.__name__}(size={self.size})"

    #internal methods to read|write the data fields in the container
    def _get_field(self, name):
        return self._data[name]
    
    def _set_field(self, name, value):
        """On assignment to field, the value gets converted to the array according to field dtype, 
        and broadcasted to expected shape"""
        #check if the input value is a structured array
        if isinstance(value, np.ndarray) and value.dtype.names is not None:
            #convert it to a plain array 
            value = value.view(value.dtype[0]).reshape(self.size,-1)
        #try to assign the field:
        dtype = self._data.dtype[name]
        target_shape = (self.size,) + dtype.shape
        value = np.asarray(value, dtype=dtype.base)
        value = np.broadcast_to(value, target_shape)
        self._data[name] = value
        return value

    @property
    def size(self):
        return len(self)

    @property
    def data(self):
        return self._data
    def __eq__(self, other):
        return ((self.__class__ == other.__class__)
                and (self.size == other.size)
                and np.all(self.data == other.data)
               )
        
    def __iter__(self):
        return iter(self.data)
    @classmethod
    def from_structarray(cls, data:np.ndarray):
        """Create an instance of this class with the given array as data.
        Raises:
            TypeError, if data.dtype != cls.dtype
        """
        if data.dtype!=cls._dtype:
            raise TypeError(f"Cannot initialize {cls.__name__}: expected dtype={cls._dtype} but got {data.dtype=}")
        result = cls(size=0)
        result._data = data
        return result

    @classmethod
    def from_array(cls, array:np.ndarray, allow_expanded=True, allow_incomplete=True):
        """convenience method from reading the StructData from incomplete data stored in the file.
        Parameters
        ----------
        allow_expanded:bool 
            If true, will try to expand this class to match the given array
        allow_incomplete:bool
            If true, will try initialize the class with the given data, ignoring the extra fields, and using default values for the missing fields.
        """
        array = np.asarray(array)
        if array.dtype==cls._dtype:
            return cls.from_structarray(array)
        #Trying to make the dtype 
        if allow_expanded:
            # Handling expanded arrays
            shapes_arr = {f: v[0].shape for f,v in array.dtype.fields.items()}
            shapes_cls = {f: v[0].shape for f,v in cls._dtype.fields.items()}
            
            fields_to_expand = {f: shape[0] for f,shape in shapes_arr.items() 
                                if shape!=shapes_cls[f]}       
            if fields_to_expand:
                expand_values = set(fields_to_expand.values())
                if len(expand_values) != 1:
                    raise ValueError(f"Incompatible expansion dimensions: {expand_values}")
                cls = cls._with_expanded_dimensions(n=expand_values.pop(),
                                                    expand_fields=list(fields_to_expand)
                                                   )
        
        # Creating object
        fields_match = set(cls.field_names) == set(array.dtype.names)
        if fields_match:
            return cls.from_structarray(array[list(cls.field_names)])
            
        if allow_incomplete:
            available_fields = {k: array[k] for k in array.dtype.names if k in cls.field_names}
            return cls(array.size, **available_fields)
        else:
            raise ValueError(f"Cannot create structure with fields {set(array.dtype.names)} - expected {set(cls.field_names)-set(cls.field_names)}. Try calling with  'allow_incomplete=True' flag")
                             
    @classmethod
    def concatenate(cls, objects:list['StructData'], allow_expanded=True, allow_incomplete=True):
        """Create an instance of this class, concatenating several StructData objects
        Raises:
            TypeError, if data.dtype != cls.dtype
        """
        if len(objects)!=0:
            data = np.concatenate([o.data for o in objects]) 
            return cls.from_array(data, allow_expanded, allow_incomplete)
        else:
            return cls(size=0)
        
    @classmethod
    def _with_expanded_dimensions(cls, n:int, expand_fields = ['pos_m', 'direction']):
        """Create a new subclass, with the expanded shapes of the given fields"""
        
        def expand_dtype(dtype, n:int, expand_fields:list[str]):
            """expand dtype for the given fields, and return a new dtype"""
            new_dtype = []
            for name in dtype.names:
                fdtype = dtype[name]
                if name in expand_fields:
                    new_dtype+=[(name, fdtype.base, (n, *fdtype.shape))]
                else:
                    new_dtype+=[(name, fdtype)]
            return np.dtype(new_dtype)
        
        class ExpandedSubclass(cls):
            _dtype=expand_dtype(cls._dtype, n, expand_fields)
        ExpandedSubclass.__name__ = f"{cls.__name__}_{n}"
        ExpandedSubclass.__module__=cls.__module__
        ExpandedSubclass.data_save = cls.data_save
        return ExpandedSubclass

    def expand_dimensions(self, n:int, expand_fields = ['pos_m', 'direction']):
        """Create a copy of this object with expanded dimensions for given fields"""
        new_cls = self._with_expanded_dimensions(n, expand_fields)
        #expand values, where needed
        fields = {name:getattr(self,name) for name in self.field_names}
        for name in expand_fields:
            fields[name] = np.expand_dims(fields[name],axis=1)
        #create the new object with expanded dtype, filled with the same data
        expanded = new_cls(size=self.size, **fields)
        return expanded

    def __getitem__(self, key):
        sel_data = self.data[key]
        if(sel_data.dtype==self._dtype):
            #return this class instance, pointing to the same data
            result = self.__class__(size=0)
            result._data = sel_data
            return result
        else:
            return sel_data
            
    def data2writer(self) -> np.ndarray:
        return self.data[list(self.data_save)]
        

class StructContainer(BaseConfig):
    """A container class to provide access to the multiple data fields inside it.
    It is based on Python dataclasses
    """
    def __init_subclass__(cls, **kwargs):
        """Initialize subclass and generate structured dtype from annotations.
        Automatically generates `_dtype` class attribute based on field type annotations.
        """
        super().__init_subclass__(**kwargs)
        #define the important variables
        cls.field_names = list(cls.__annotations__)
        #wrap in the dataclass decorator
        cls = dataclass(cls)

        # add data selector
        FieldSelector().add_to_class(cls, name='data_save')
        
    def data2writer(self) -> dict:
        return {name:getattr(self, name) for name in self.data_save}
            