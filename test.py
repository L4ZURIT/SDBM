import itertools
import numpy as pd

data = {
    'age': [0.5,56,8], 
    'var': ['a0','b','c']
    }

print(data.values())

print(list(map(list, itertools.zip_longest(*data.values(), fillvalue=None))))

