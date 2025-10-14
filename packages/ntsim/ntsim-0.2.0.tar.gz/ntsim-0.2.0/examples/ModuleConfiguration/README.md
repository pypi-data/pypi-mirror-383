# Module Configuration with Command Line Arguments

This example demonstrates how to use command line arguments to configure a class in a Python program. The main components of this example are:

1. **AnyClass**: A sample class that we want to configure.
2. **AnyClassConfig**: A dataclass that represents the configuration for `AnyClass`.
3. **Command Line Arguments**: Using `configargparse` to parse command line arguments.
4. **NestedNamespace**: A utility from `ntsim.utils.arguments_handling` that allows for nested argument parsing.

## Components

### AnyClass

This is a sample class that we want to configure using command line arguments. It takes an instance of `AnyClassConfig` during initialization.

### AnyClassConfig

A dataclass that holds the configuration for `AnyClass`. It has the following fields:

- `general_var1`: An integer.
- `general_var2`: A string.
- `anyclass_var1`: A float.
- `anyclass_var2`: A list of integers.

### Command Line Arguments

We use `configargparse` to define and parse command line arguments. The arguments are defined in a nested manner using dots (`.`) to separate the levels. For example, `--general.var1` and `--anyclass.var1`.

### NestedNamespace

This utility allows us to parse command line arguments in a nested manner. Instead of accessing arguments using `args['general.var1']`, we can use `args.general.var1`.

## How to Run

To run the example, use the following command:

```
python3 ModuleConfig.py --general.var1 10 --general.var2 "example" --anyclass.var1 3.14 --anyclass.var2 1 2 3 4
```

This will print the parsed command line arguments and the configuration of `AnyClass`.

## Key Takeaways

- Using `configargparse` allows for flexible command line argument parsing.
- `NestedNamespace` provides a clean way to access nested arguments.
- Dataclasses provide a structured way to represent configurations.
