import configargparse
from ntsim.utils.arguments_handling import NestedNamespace
parser = configargparse.get_argument_parser()
parser.add('--module1.input', type=str, default='input1', help='an input for module1')
parser.add('--module2.input', type=str, default='input2', help='an input for module1')
opts = parser.parse_args(namespace=NestedNamespace())

print(opts)
