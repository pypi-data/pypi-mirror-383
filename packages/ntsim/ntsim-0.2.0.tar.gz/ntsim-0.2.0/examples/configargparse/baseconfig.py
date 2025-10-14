from ntsim.Base.BaseConfig import BaseConfig
import configargparse

class Module1(BaseConfig):
    arg_dict = {'x': {'type': int, 'default': 1, 'help': 'x parameter'},}

class Module2(BaseConfig):
    arg_dict = {'y': {'type': str, 'default': 'test', 'help': 'y parameter'},}

class Factory:
    def __init__(self):
        self.modules = [Module1, Module2]

    def add_module_args(self, parser):
        for module in self.modules:
            module.add_args(parser)

def main():
    factory = Factory()
    parser = configargparse.ArgParser()

    # Add common arguments
    parser.add_argument('--log-level', type=str, default='INFO', help='Logging level')

    # Add module-specific arguments
    factory.add_module_args(parser)

    opts = parser.parse_args()

    print(parser.format_values())
    m = Module1()
    m.configure(opts)
    print(f'dict with all arguments: {m.arg_dict}')
    print(f'now module has a variable x={m.x}')

if __name__ == "__main__":
    main()
