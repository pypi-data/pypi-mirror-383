# Nested Argument Parsing with `arguments_grouped`

The `arguments_grouped` module provides a way to parse command-line arguments into a nested namespace structure. This allows for a more organized and hierarchical representation of command-line options, especially when dealing with complex applications that have multiple sub-components or modules, each with its own set of configurations.

## Concept

Traditional argument parsing in Python using `argparse` results in a flat namespace. For instance, if you have arguments like `--input`, `--output`, and `--config`, the resulting namespace will have attributes `input`, `output`, and `config`.

The `arguments_grouped` approach allows for arguments to be grouped hierarchically using a dot notation. For example, `--module1.input` and `--module2.input` can be parsed into a nested structure where `module1` and `module2` are namespaces containing their respective `input` attributes.

## Implementation

The core of this functionality is the `NestedNamespace` class, which overrides the `__setattr__` method to create nested `argparse.Namespace` objects based on the dot notation in the argument names.

## Example

Consider the following code:

```python
import configargparse
from ntsim.utils.arguments_handling import NestedNamespace
parser = configargparse.get_argument_parser()
parser.add('--module1.input', type=str, default='input1', help='an input for module1')
parser.add('--module2.input', type=str, default='input2', help='an input for module1')
opts = parser.parse_args(namespace=NestedNamespace())

print(opts)
```

If you run this script with the following arguments:

```
$ python3 your_script.py --module1.input data1.txt --module2.input data2.txt
```

The output will be:

```
Namespace(module1=Namespace(input='data1.txt'), module2=Namespace(input='data2.txt'))
```

This shows that the arguments have been grouped into nested namespaces based on the dot notation.

## Benefits

- **Organized Configuration**: Especially useful for large applications with multiple components, each having its own set of configurations.
- **Readability**: The dot notation provides a clear indication of the hierarchy and relationship between arguments.
- **Flexibility**: Easily extendable to add more nested configurations without major changes to the existing argument parsing logic.
