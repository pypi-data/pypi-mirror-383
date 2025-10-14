import argparse

class NestedNamespace(argparse.Namespace):
    def __init__(self, **kwargs):
        super(NestedNamespace, self).__init__(**kwargs)
    def __setattr__(self, name, value):
        keys = name.split('.')
        d = self
        for key in keys[:-1]:
            if not hasattr(d, key) or not isinstance(getattr(d, key), argparse.Namespace):
                d.__dict__[key] = argparse.Namespace()
            d = getattr(d, key)
        d.__dict__[keys[-1]] = value
