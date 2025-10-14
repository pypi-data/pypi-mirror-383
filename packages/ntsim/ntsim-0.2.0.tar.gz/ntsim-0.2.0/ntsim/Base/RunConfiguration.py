import yaml

class RunConfiguration(dict):
    """A container of the run configuration"""
    def __init__(self, **parameters):
        super().__init__(parameters)

    @classmethod
    def from_flatdict(cls, flat_dict):
        result = {}
        for key, value in flat_dict.items():
            branch = result
            *path, last = key.split('.')
            for part in path:
                branch = branch.setdefault(part, {})
            branch[last] = value
        return cls(**result)

    def cleanup(self):
        """this is a temporary fix for the case when we have too many
        config entries, not only the ones selected by '*_name' entries"""
        used_names = [value for key,value in self.items() if key.endswith('_name')]
        del_keys = []
        
        result = {}
        for key,value in self.items():
            if key.endswith('_name'):
                if value in self:
                    result[key.removesuffix('_name')] = {value: self[value]}
                else:
                    result[key] = value
                
            elif (not isinstance(value, dict)) or (key.startswith('g')):
                result[key] = value
                continue                
        self.clear()
        self.update(result)
            
    @classmethod
    def from_namespace(cls, opts):
        return cls.from_flatdict(opts.__dict__)

    def to_yaml(self):
        def _list_representer_one_line(dumper, data):
            return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
        yaml.add_representer(list, _list_representer_one_line, Dumper=yaml.Dumper)
        yaml.add_representer(tuple, _list_representer_one_line, Dumper=yaml.Dumper)
        s = yaml.dump(dict(self), sort_keys=False, default_flow_style=False, indent=4)
        return s