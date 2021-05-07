
import numpy as np

''' helper fx'''
def xy_around(x,y,r=1,inv=False,ext=False):
    axy = []
    if inv:
        for j in range(-r,r+1,1):
            for i in range(-r,r+1):
                axy.append([y+j,x+i])
    else:
        for j in range(r,(-r-1),-1):
            for i in range(-r,(r+1)):
                axy.append([y+j,x+i])
    if ext:
        size = 2**r+1
        for dr in range(size-r,0,-1):
            del(axy[int(size*dr+1):int(size*(dr+1)-1)])
    return np.asarray(axy)



'''
# south-east
se1 = [[0,0,1],[1,0,1],[0,1,1]]
se2 = [[1,0,0],[0,1,1],[1,1,0]]
se3 = [[0,1,0],[0,0,1],[1,1,1]]
se4 = [[1,0,1],[0,1,1],[0,1,0]]
se = [se1,se2,se2,se4]

# south-west
sw1 = [[1,0,0],[1,0,1],[1,1,0]]
sw2 = [[0,0,1],[1,1,0],[0,1,1]]
sw3 = [[0,1,0],[1,0,0],[1,1,1]]
sw4 = [[1,0,1],[0,1,1],[0,1,0]]
sw = [sw1,sw2,sw3,sw4]

# north-east
ne1 = [[0,1,1],[1,0,1],[0,0,1]]
ne2 = [[1,1,0],[0,1,1],[1,0,0]]
ne3 = [[1,1,1],[0,0,1],[0,1,0]]
ne4 = [[0,1,0],[0,1,1],[1,0,1]]
ne = [ne1,ne2,ne3,ne4]

# north-west
nw1 = [[1,1,0],[1,0,1],[1,0,0]]
nw2 = [[0,1,1],[1,1,0],[0,0,1]]
nw3 = [[1,1,1],[1,0,0],[0,1,0]]
nw4 = [[0,1,0],[1,1,0],[1,0,1]]
nw = [nw1,nw2,nw3,nw4]
'''
