import numba
from numba import njit, types
import numpy as np

@njit
def f1(vars, opts):
    x, y = vars
    opt1, opt2 = opts
    return (x + y) * opt1* opt2

@njit
def f2(vars, opts):
    x, y = vars
    opt1, opt2 = opts
    return (2 * x + y) * opt1 * opt2

# Define the function type
func_type = types.float64(types.float64[:], types.float64[:]).as_type()

# Create a typed list to hold the function pointers
f_list = numba.typed.List.empty_list(func_type)
f_list.append(f1)
f_list.append(f2)

# Define the jitclass
@numba.experimental.jitclass([('funcs', types.ListType(func_type))])
class Handler:
    def __init__(self, funcs):
        self.funcs = funcs

# Create an instance of the Handler class
h = Handler(f_list)

# Test the functions
vars = np.array([1.0, 2.0])
opts = np.array([1.0, 3.0])

@njit
def dump(l,vars,opts):
    for i,f in enumerate(l):
        a = l[i]
        r = f(vars,opts)
        print(r)
print(f_list)
dump(f_list,vars,opts)


for i, f in enumerate(f_list):
    print(i,f)
for f in h.funcs:
    if f == f1:
        print(f(vars, opts))
    elif f == f2:
        print(f(vars, opts))
