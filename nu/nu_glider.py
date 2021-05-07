
import numpy as np
from nu_fx import xy_around

class Glider:
    def __init__(self,genotype,st0,o0,x0=None,y0=None):
        self.gt = genotype.map
        self.eos = [o0]*9
        self.domain = np.zeros((7,7))
        self.domain[1:6,1:6] = st0
        # pos (orientation: 0=north, 1=east, 2=south, 3=west)
        self.x = x0
        self.y = y0
        # elements rel locs and init orientations
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        # to compute motion (slot for orientations)
        self.motion_T = 2

    def update(self,gl_domain):
        new_domain = np.zeros((7,7))
        motion = [0]*4
        # core
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain
            e_in = np.rot90(gl_domain[i-1:i+2,j-1:j+2],self.eos[ei]).flatten()
            bi = int(''.join(str(int(i)) for i in e_in),2)
            # create response if theres isn't one
            if not self.gt[bi]:
                #self.gt[bi] = np.random.randint(0,8)
                import pdb; pdb.set_trace()
            sig,rm,lm = self.gt[bi]
            # update
            new_domain[i][j] = sig
            self.eos[ei] = (self.eos[ei]+rm-lm)%4
            if rm+lm == 2:
                self.motion[self.eos[ei]] += 1
        # membrane
        for ei,[i,j] in enumerate(self.me_ij):
            me_in = np.sum(gl_domain[i-1:i+2,j-1:j+2])
            if ei==0 or ei==4 or ei==11 or ei==15:
                th = 1
            elif ei==2 or ei==7 or ei==8 or ei==13:
                th = 3
            else:
                th =2
            new_domain[i][j] = 1 if me_in > th else 0
        # motion
        mx = motion[1] - motion[3]
        my = motion[0] - motion[2]
        if max(abs(mx),abs(my)) > self.motion_T:
            if abs(mx) > abs(my):
                self.x += mx/abs(mx)
            else:
                self.y -= my/abs(my)
