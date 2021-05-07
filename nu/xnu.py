
import numpy as np

class Element:
    def __init__(self,gt,o0,s0):
        # genotype
        self.u = gt
        # self.x,self.y = x0,y0
        # 0=north, 1=east, 2=south, 3=west
        self.o = o0
        # signaling: 1/0
        self.sig = s0

    def update(self,env):
        # adjust env info according to current orientation
        ein = np.rot90(env,self.o).flatten()
        # convert to binary to map to output
        bi = int(''.join(str(int(i)) for i in ein),2)
        # search for response. If it isn't one, create it
        if not self.u[bi]:
            self.u[bi] = np.random.randint(0,8)
        # update
        self.sig,rm,lm = np.binary_repr(self.u[bi],3)
        # turn: rm=1 > right, lm=1 > left
        self.o = (self.o+rm-lm)%4
        # motion
        mx = 1 if (rm+lm)>1 else 0
        return mx

'''update according to re-oriented input'''
def xupdate(self,env):
    self.motion = [0]*4
    # core
    core_domain = np.zeros((7,7))+self.domain
    for ei,[i,j] in enumerate(self.ce_ij):
        # re-oriented surrounding space + recurrent state
        e_in = np.rot90(core_domain[i-1:i+2,j-1:j+2],self.eos[ei]).flatten()
        # search for response in gt
        bi = int(''.join(str(int(i)) for i in e_in),2)
        # create response if theres isn't one
        if not self.gt[bi]:
            self.gt[bi] = np.random.randint(0,8)
        esig,rm,lm = [int(ri) for ri in np.binary_repr(self.gt[bi],3)]
        # update element
        self.domain[i][j] = esig
        # 0,0:stay - 1,0:turn right, 0,1:turn left - 1,1:move forward
        self.eos[ei] = (self.eos[ei]+rm-lm)%4
        if rm+lm > 1:
            self.motion[self.eos[ei]] += 1
    # membrane
    mem_domain = np.zeros((7,7))+env
    mem_domain[2:5,2:5] = self.domain[2:5,2:5]
    for i,j in self.me_ij:
        # 0 if any activation around (not itself), 1 otherwise
        me_in = np.sum(mem_domain[i-1:i+2,j-1:j+2])-mem_domain[i][j]
        self.domain[i][j] = 0 if me_in > 0 else 1
    self.motion_fx()

'''update according to sum + state'''
    def update(self,gl_domain):
        self.motion = TODO
        new_domain = np.zeros((7,7))
        # core
        for ei,[i,j] in enumerate(self.ce_ij):
            # sum of surrounding signals
            esum = np.sum(gl_domain[i-1:i+2,j-1:j+2])-gl_domain[i][j]
            # state
            st = self.sts[ei]+gl_domain[i][j]
            self.sts[ei] = 0 if int(st)==1 else st
            # response index ((maxsum+1)*st)+sum: [0,17]
            ri = 9*int(st)+esum
            # response from map
            sig,rm,lm = self.gt[ei][ri]
            # update signal
            new_domain[i][j] = sig
            # update orientation and motion intention


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

###
