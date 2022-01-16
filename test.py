import numpy as pd


data = {
    'age': [0.5,56,8], 
    'var': ['a0','b','c']
    }

vals = pd.array(list(data.values())).transpose()

print("type = ", type(vals[0][0]))


ans = ", ".join("("+", ".join(val[i] if not str(val[i]).isidentifier() else "'"+val[i]+"'" for i in range(len(val)))+")" for val in vals)
print(ans)

#print(str(vals).replace("[", "(").replace("]", ")")[1:-1])


