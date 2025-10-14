import configargparse
from dataclasses import dataclass
from typing import List
from ntsim.utils.arguments_handling import NestedNamespace

@dataclass
class AnyClassConfig:
    general_var1: int
    general_var2: str
    anyclass_var1: float
    anyclass_var2: List[int]

class AnyClass:
    def __init__(self, config: AnyClassConfig):
        self.config = config

    def print_config(self):
        print(self.config)

def combine_options(args) -> AnyClassConfig:
    return AnyClassConfig(
        general_var1=args.general.var1,
        general_var2=args.general.var2,
        anyclass_var1=args.anyclass.var1,
        anyclass_var2=args.anyclass.var2
    )

if __name__ == '__main__':
    parser = configargparse.get_argument_parser()
    parser.add_argument('--general.var1', type=int, required=True, help='A general variable 1')
    parser.add_argument('--general.var2', type=str, required=True, help='A general variable 2')
    parser.add_argument('--anyclass.var1', type=float, required=True, help='Variable 1 specific to AnyClass')
    parser.add_argument('--anyclass.var2', type=int, nargs='+', required=True, help='Variable 2 specific to AnyClass')

    args = parser.parse_args(namespace=NestedNamespace())
    print("Parsed Command Line Arguments:")
    print(args)

    config = combine_options(args)
    any_class_instance = AnyClass(config)
    any_class_instance.print_config()
