
import numpy as np

# convert array > binary > int
def arr2int(arr,r=None):
    if r:
        arr = np.rot90(arr,r)
    x = int(''.join(arr.flatten().astype(int).astype(str)),2)
    return x


    
