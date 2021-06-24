
import numpy as np
from copy import deepcopy
from collections import defaultdict
from nu_fxs import *

#TODO: replace random response for something more sensible (viability based dists?)
#TODO: gt: assign values from occurrences for a exgt distribution, so to pass responses for next generarions
# in this way unnecesar things should get discarded

'''dx,mx0,cx0 -> mx : mx,cx0 -> cx : cx -> dx+1 : ...'''
class Glider:
    def __init__(self,gt,st0=12,x0=25,y0=25):
        # element gt instructions
        self.exgt = deepcopy(gt.exgt)
        # glider behavioral data
        self.cycles = deepcopy(gt.cycles)
        self.txs = deepcopy(gt.txs)
        self.dxs = deepcopy(gt.dxs)
        # updating modes for core and membrane
        self.cx_mode = gt.cx_mode
        self.mx_mode = gt.mx_mode
        # glider trial sts (orientation: 0=north, 1=east, 2=south, 3=west)
        self.st = None
        self.core = None
        self.membrane = None
        self.eos = None
        self.ems = None
        self.om = None
        self.i,self.j = x0,y0
        self.erxs = {}
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        # threshold for motion
        self.mt = 2
        # trial data
        self.t = 0
        self.states = []
        self.ex_sts = [0]
        self.core_sts = []
        self.memb_sts = []
        self.env_sts = [0]
        self.resps = defaultdict(set)
        self.loc = [[x0,y0]]
        self.dxom = []
        self.tx_seq = []
        self.loops = set()
        self.set_cfg(st0)

    '''update every element for a new global state'''
    def update(self,gl_domain):
        # update membrane and core states
        self.gl_membrane(gl_domain,mode=self.mx_mode)
        self.gl_core(gl_domain,mode=self.cx_mode)
        # general st (astype to avoid np inheritane issues)
        self.st = self.membrane.astype(int)
        self.st[1:4,1:4] = self.core.reshape(3,3)
        self.states.append(self.st)
        # system's motion reaction
        self.gl_motion()
        # data for analysis
        self.gl_data(gl_domain)
        self.t += 1

    '''update membrane'''
    def gl_membrane(self,domain,mode=""):
        # initialize membrane as (7x7) to fit domain coords
        self.membrane = np.zeros((7,7)).astype(int)
        # if nothing from core + anything from outside
        if mode=="basic":
            # corners
            if domain[2][2]==0:
                self.membrane[1][1] = np.sum([domain[1][0],domain[0][0],domain[0][1]])
            if domain[2][4]==0:
                self.membrane[1][5] = np.sum([domain[0][5],domain[0][6],domain[1][6]])
            if domain[4][2]==0:
                self.membrane[5][1] = np.sum([domain[5][0],domain[6][0],domain[6][1]])
            if domain[4][4]==0:
                self.membrane[5][5] = np.sum([domain[6][5],domain[6][6],domain[5][6]])
            # remaining membrane elements (e2,e3,e4 for each wall)
            for j in range(2,5):
                if np.sum(domain[2,max(2,j-1):min(j+2,5)])==0:
                    self.membrane[1][j] = np.sum(domain[0,j-1:j+2])
                if np.sum(domain[4,max(2,j-1):min(j+2,5)])==0:
                    self.membrane[5][j] = np.sum(domain[6,j-1:j+2])
            for i in range(2,5):
                if np.sum(domain[max(2,i-1):min(i+2,5),2])==0:
                    self.membrane[i][1] = np.sum(domain[i-1:i+2,0])
                if np.sum(domain[max(2,i-1):min(i+2,5),4])==0:
                    self.membrane[i][5] = np.sum(domain[i-1:i+2,6])
            # if higher than 0: 1
            self.membrane = np.where(self.membrane[1:6,1:6]>0,1,0)
        # ~ potential diference (external-internal)
        elif mode=="delta":
            # north and south elements
            for j in range(1,6):
                self.membrane[1][j] += np.sum(domain[0,j-1:j+2])-np.sum(domain[2,max(2,j-1):min(j+2,5)])
                self.membrane[5][j] += np.sum(domain[6,j-1:j+2])-np.sum(domain[4,max(2,j-1):min(j+2,5)])
            # east and west elements
            for i in range(1,6):
                self.membrane[i][1] += np.sum(domain[i-1:i+2,0])-np.sum(domain[max(2,i-1):min(i+2,5),2])
                self.membrane[i][5] += np.sum(domain[i-1:i+2,6])-np.sum(domain[max(2,i-1):min(i+2,5),4])
            # corners (to avoid double sum from domain's corners)
            self.membrane[1][1] -= domain[0][0]
            self.membrane[1][5] -= domain[0][6]
            self.membrane[5][1] -= domain[6][0]
            self.membrane[5][5] -= domain[6][6]
            # if outside > inside input:1, otherwise:0
            self.membrane = np.where(self.membrane[1:6,1:6]>0,1,0)
        # anything from outside
        elif mode=="all":
            mdomain = deepcopy(domain)
            mdomain[1:6,1:6] = 0
            for [i,j] in self.me_ij:
                if np.sum(mdomain[i-1:i+2,j-1:j+2])>0:
                    self.membrane[i][j] = 1
            self.membrane = self.membrane[1:6,1:6]
        else:
            raise Exception("no mode for membrane")

    '''update core'''
    def gl_core(self,domain,mode=""):
        self.core = np.zeros(9).astype(int)
        self.ems = np.zeros(4).astype(int)
        ers = []
        # responses given element genotypes
        if mode=="genotype":
            for ei,[i,j] in enumerate(self.ce_ij):
                # re-oriented element domain
                eo = self.eos[ei]
                e_in = arr2int(domain[i-1:i+2,j-1:j+2],rot=eo)
                # create response if theres isn't one (dict of responses)
                ri = "gt"
                if not e_in in self.exgt.keys():
                    ri = "new"
                    self.exgt[e_in] = list(np.random.randint(0,2,size=(3)))
                sx,rm,lm = self.exgt[e_in]
                ers.append((eo,e_in,ri,sx,rm,lm))
                # activation
                self.core[ei] = sx
                # motor response
                if lm==rm==1:
                    self.ems[self.eos[ei]] += 1
                else:
                    self.eos[ei] = (self.eos[ei]+rm-lm)%4
            self.ex_sts.append(ers)
        # responses based on the CA version
        elif mode=="automata":
            for ei,[i,j] in enumerate(self.ce_ij):
                # signalings
                e_in = np.sum(domain[i-1:i+2,j-1:j+2])-domain[i][j]
                if domain[i][j]==0:
                    if e_in==3:
                        self.core[ei]=1
                else:
                    if e_in==2 or e_in==3:
                        self.core[ei]=1
            # motion (0:north, 1:east, 2:south, 3:west)
            self.ems[0] = np.sum(self.core.reshape(3,3)[0,:])
            self.ems[1] = np.sum(self.core.reshape(3,3)[:,2])
            self.ems[2] = np.sum(self.core.reshape(3,3)[2,:])
            self.ems[3] = np.sum(self.core.reshape(3,3)[:,0])
        else:
            raise Exception("no mode for core")

    '''bounded group motion'''
    def gl_motion(self):
        # select higher sum and move if higher than motion threshold
        dx = self.ems[1]-self.ems[3]
        dy = self.ems[0]-self.ems[2]
        # om: 0:stay, 1:E, 2:S, 3:W, 4:N
        om0,xom,self.om = self.om,0,0
        if abs(dx)>abs(dy):
            if abs(dx)>=self.mt:
                self.j += int(dx/abs(dx))
                self.om = 1 if int(dx/abs(dx))>0 else 3
        elif abs(dy)>abs(dx):
            if abs(dy)>=self.mt:
                self.i += int(-dy/abs(dy))
                self.om = 4 if int(-dy/abs(dy))>0 else 2
        # xom: (0:stay, -1:left, 1:right, 2:forward, -2:back, 3:start, -3:stop)
        dom = self.om-om0
        if om0==self.om==0:
            xom=0
        elif self.om==0:
            xom=-3
        elif om0==0:
            xom=3
        elif dom==0:
            xom=2
        elif abs(dom)==1:
            xom=dom
        elif abs(dom)==2:
            xom=-2
        elif abs(dom)==3:
            xom=2-dom
        else:
            import pdb; pdb.set_trace()
            raise Exception("motion change error")
        self.loc.append([self.i,self.j])
        self.dxom.append([om0,xom,self.om])

    '''data for visualization and analysis'''
    def gl_data(self,gl_domain):
        # core
        cx0 = self.core_sts[-1]
        cx = arr2int(self.core)
        self.core_sts.append(cx)
        # membrane
        mx0 = self.memb_sts[-1]
        mx = ext2int(self.membrane)
        self.memb_sts.append(mx)
        # encountered dash pattern
        dx0 = ext2int(gl_domain)
        self.env_sts.append(dx0)
        self.dxs.add(dx0)
        # motion based orientation change
        om0,xom,om = self.dxom[-1]
        # trial responses
        self.resps[(cx0,mx0,dx0)].add((cx,mx,xom))
        # txs v2: transition is in cycle
        if (cx0,mx0,dx0) in self.cycles and (cx,mx)==self.cycles[(cx0,mx0,dx0)]:
            # if transition was occurring
            if len(self.tx_seq)>0:
                self.tx_seq.append((cx0,mx0,dx0,om0,xom,om,cx,mx,self.t))
                self.tx_seq.append((cx,mx))
                d0 = self.tx_seq[0][2]
                self.txs[d0].append(self.tx_seq)
                # element responses
                t0 = self.tx_seq[0][-1]
                for ex_st in self.ex_sts[t0:]:
                    for ei_st in ex_st:
                        e_in = ei_st[1]
                        e_ri = ei_st[3:]
                        self.erxs[e_in] = e_ri
                # reset
                self.tx_seq = []
        else:
            # if not in cycle, keep tx seq growing
            self.tx_seq.append((cx0,mx0,dx0,om0,xom,om,cx,mx,self.t))

    '''search for loops (possible transients/cycles)'''
    def gl_loops(self):
        for i,[ci,mi,di] in enumerate(zip(self.core_sts,self.memb_sts,self.env_sts)):
            cxi = np.where(self.core_sts==ci,1,0)
            mxi = np.where(self.memb_sts==mi,1,0)
            dxi = np.where(self.env_sts==di,1,0)
            lxi = cxi*mxi*dxi
            if np.sum(lxi)>1:
                cx = np.where(self.core_sts==ci,self.core_sts,0)
                mx = np.where(self.memb_sts==mi,self.memb_sts,0)
                dx = np.where(self.env_sts==di,self.dashes,0)
                loop = np.vstack((cx,mx,dx))
                self.loops.add(loop)

    '''allocate glider starting from some known cfg'''
    def set_cfg(self,st0):
        # initial states (assuming initial empty env)
        if st0==14:
            act=[3,1,2,5,8]     # east -> north
        elif st0==12:
            act=[3,7,2,5,8]     # east -> south
        elif st0==21:
            act=[1,5,6,7,8]     # south -> east
        elif st0==23:
            act=[1,3,6,7,8]     # south -> west
        elif st0==34:
            act=[0,3,6,1,5]     # west -> north
        elif st0==32:
            act=[0,3,6,7,5]     # west -> south
        elif st0==41:
            act=[0,1,2,5,7]     # north -> east
        elif st0==43:
            act=[0,1,2,3,7]     # north -> west
        else:
            raise Exception("invalid initial cfg")
        cxi = np.zeros(9).astype(int)
        for ei in act:
            cxi[ei] = 1
        self.st = np.zeros((5,5)).astype(int)
        self.st[1:4,1:4] = cxi.reshape(3,3)
        # initial orientations (changing, then fixed-start ones)
        self.eos = np.zeros(9).astype(int)
        eos0 = int(str(st0)[0])%4
        self.eos += eos0
        self.eos[1] = 0
        self.eos[3] = 3
        self.eos[5] = 1
        self.eos[7] = 2
        # oriented motion (assuming cycle)
        self.om = int(str(st0)[1])%4
        # initial data
        self.states.append(self.st)
        cx = arr2int(cxi)
        self.core_sts.append(cx)
        self.memb_sts.append(0)









###
