from __future__ import annotations #compatibility for python3.10
import numpy as np
from typing import Generic, Type, Generator, Any, Tuple, TypeVar
from ntsim.IO import gEvent, gParticles, gTracks, gHits, gPhotons
from ntsim.IO.Base.StructData import StructData
from ntsim.Base import RunConfiguration
import yaml
import h5py
import functools


class LazyDict(dict):
    """A dict with the lazy evaluation.
    If a value contains a function, it will be called on the first access"""
    def _getitem_base(self, key):
        """get item without evaluating callback"""
        return super().__getitem__(key)
    def __getitem__(self, key):
        """get item evaluating callback"""
        val = self._getitem_base(key)
        if callable(val):
            val = val()
            #self.__setitem__(key, val)
        return val
        
    def get_static(self) -> dict:
        """evaluate all callbacks, and produce a regular dict"""
        return {key:val.get_static() if isinstance(val,self.__class__) else val
                  for key,val in self.items()}
    def items(self) -> Generator[Tuple[str, Any]]:
        for key in self:
            yield key, self[key]
    def values(self) -> Generator[Any]:
        for key in self:
            yield self[key]
            
    def values_flat(self) -> Generator[Any]:
        for data in self.values():
            if isinstance(data, LazyDict):
                yield from data.values_flat()
            else:
                yield data
    def __repr__(self):
        """string representation without evaluating callbacks"""
        items = {key:self._getitem_base(key) for key in self}
        s = self.__class__.__name__+': {'
        items = []
        for key in self:
            val = self._getitem_base(key)
            if callable(val):
                val = '<callable>'
            items.append(f'{key}:{val}')
        s+= ', '.join(items) +'}'
        return s


T = TypeVar('T', bound=StructData)

class LazyStruct(LazyDict, Generic[T]):
    """A lazy evaluation class for dicts, which contain a certain data structure (StructData subclass).
    It must be initialized with a subscribed type, i.e.
      LazyStruct[gTracks](...)
    
    Useful methods:

    all() - returns the concatenated data from all keys
    bunches(bunch_size) - loop over underlying data in bunches of given size
    """
    _base: Type[T] = None

    def __init__(self, *args, **kwargs):
        if self._base is None: 
            raise TypeError(
                f"{self.__class__.__name__} must be subscripted with a base type. "
                f"Use {self.__class__.__name__}[YourBaseType] instead."
            )
        super().__init__(*args, **kwargs)

    def __class_getitem__(cls, base_type: Type[T]) -> Type['LazyStruct']:
        """Create a specialized LazyStruct class with the given base type"""
        class_name = f"LazyStruct[{base_type.__name__}]"
        
        # Create the new class
        class new_class(cls):
            _base = base_type
            
            def count(self) -> int:
                """Read all the data and return total number of elements"""
                return sum([v.size for v in self.values_flat()])
                
            def all(self) -> base_type:
                """Read all underlying data and concatenate it into a single object"""
                return self._base.concatenate(list(self.values_flat()))
                
            def bunches(self, bunch_size=1000) -> Generator[base_type]:
                """Loop over underlying data in bunches of given size. Yields the 'base_type' objects of size 'bunch_size' or smaller"""
                N_collected = 0
                datas = []
                for data in self.values_flat():
                    N_collected += data.size
                    datas.append(data)
                    if N_collected >= bunch_size:
                        result = self._base.concatenate(datas)
                        while result.size >= bunch_size:
                            yield result[:bunch_size]
                            result = result[bunch_size:]
                        datas = [result]
                        N_collected = result.size
                yield self._base.concatenate(datas)
                    # Set the proper name for the class
        new_class.__name__ = class_name
        new_class.__qualname__ = class_name
        new_class.__module__ = cls.__module__
        new_class.__doc__ = f"A lazy evaluation class for dicts, which contain '{base_type.__name__}' structures."
        return new_class
        
def lazy(cls):
    """A simple decorator to make container classes with LazyDicts inside"""
    class cls1(cls):
        def make_static(self):
            """evaluate all callbacks"""
            for name, val in self.__dict__.items():
                if hasattr(val, 'get_static'):
                    setattr(self, name, val.get_static())
    cls1.__name__ = cls.__name__
    cls1.__module__ = cls.__module__ 
    cls1.__qualname__ = cls.__qualname__ 
    return cls1

class h5Reader(h5py.File):
    """A class that can read the header and events from the h5 File.
    It provides access to:
    * self.geometry (structured array)
    * self.run_configuration (full configuration of the simulation)
    * self.events (a dictionary with all the events, which are loaded on demand)
    
    Example:
    ------
        #A nice interface to loop around the data
        #without thinking about internal representation
        
        with h5Reader('h5_output/events.h5') as f:
            print(f"File \"{f.filename}\" has total {len(f.events)} events")
            print(f'Geometry contained {len(f.geometry)} optical modules ')
            print(f'Primary generator configuration:')
            print(f.run_configuration['primary_generator'])
            
            for num, event in f.events.items():
                print(f'event#{num} has {event.hits['Hits'].size} hits')
    """
    def __init__(self, filename):
        super().__init__(filename)
        self._read_header()
        self._read_events()

    def _read_events(self):
        ev_prefix = "event_"
        ev_names = [k for k in self.keys() if k.startswith(ev_prefix)]
        ev_nums = [int(k.removeprefix(ev_prefix)) for k in ev_names]
        _events_names = dict(sorted(zip(ev_nums, ev_names)))
        self.events = LazyDict({key: functools.partial(self._read_event, name) 
                                for key,name 
                                in sorted(zip(ev_nums, ev_names))}
                              )

    def _read_header(self)->dict:
        cfg = self['Header/run_configuration'].asstr()[()]
        self._header_yaml = cfg
        cfg = yaml.safe_load(cfg)
        self.run_configuration = RunConfiguration(**cfg)
        if 'geometry' in self['Header']:
            self.geometry = np.array(self['Header/geometry/Geometry'])
        else:
            self.geometry = None
    
    def _read_event(self, name:str)->gEvent:
        #read the directory
        event_dir = self[name]
        def _read_recursively(cls, data:h5py.Group|h5py.Dataset):
            if isinstance(data, h5py.Dataset):
                return functools.partial(cls.from_array, data, allow_expanded=True)
            else:
                return LazyStruct[cls]({key: _read_recursively(cls, val) for key,val in data.items()})

        def _read_products(cls, data_key:str):
            if data_key not in event_dir:
                return {}
            else:
                return _read_recursively(cls, event_dir[data_key])
        
        the_event = lazy(gEvent)(
            particles = _read_products(gParticles, "particles"),
            tracks = _read_products(gTracks,"tracks"),
            hits = _read_products(gHits, "hits"),
            photons = _read_products(gPhotons, "photons")
        )
                
        return the_event