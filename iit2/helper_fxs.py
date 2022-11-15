
import numpy as np

# tensor with n matrix reps
def matrix_reps(x,n=3,m=3):
    t = np.zeros((x,n,m))
    for i in range(x):
        xmn = int2arr(i,n*m,2)
        t[i] = xmn
    return t

# convert array > binary > int
def arr2int(arr):
    xi = np.sum([x<<e for e,x in enumerate(arr.flatten().astype(int))])
    return xi

# convert int number into an array or a MxM matrix
def int2arr(n,arr_len,axes=1):
    # needs to be reversed for assignation to elements [e0,e1,e2...]
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    if axes == 2:
        d = np.sqrt(arr_len).astype(int)
        x = x.reshape(d,d)
    return x

# list of bin<->int conversions
# (to avoid calling the fxs all the time)
def bin2int(n):
    b2i = {}
    for ni in range(2**n):
        nb = int2arr(ni,arr_len=n)
        b2i[tuple(nb)] = ni
    return b2i

def int2bin(n):
    i2b = {}
    for ni in range(2**n):
        nb = int2arr(ni,arr_len=n)
        i2b[ni] = nb
    return i2b

# cell locations (domain=21, env=16, sys=5)
def ddxlocs(r):
    ij = []
    env_js = [[1,2,3],[0,1,3,4],[0,4],[0,1,3,4],[1,2,3]]
    sys_js = [[],[2],[1,2,3],[2],[]]
    for i in range(5):
        # domain
        if r==21:
            j0,jn = (1,4) if i%4==0 else (0,5)
            for j in range(j0,jn):
                ij.append([i,j])
        # environment only
        elif r==16:
            for j in env_js[i]:
                ij.append([i,j])
        # ring system
        elif r==5:
            for j in sys_js[i]:
                ij.append([i,j])
    return ij

# tensor for 2d domains
def ddxtensor(r):
    # non empty locations
    ij = ddxlocs(r)
    # tensor object
    ddx = np.zeros((5,5,2**r))
    for er,[ei,ej] in enumerate(ij):
        ezr = 2**er
        ez0 = np.zeros(ezr)
        ez1 = np.ones(ezr)
        ez01 = np.concatenate((ez0,ez1))
        dez = 2**(r-er-1)
        ezt = np.full((dez,len(ez01)),ez01).flatten()
        ddx[ei,ej,:] = ezt
    return ddx.astype(int)

# ring locations (top to bottom, left to right)
def ring_locs(i=0,j=0,r=1,hollow=True):
    locs = []
    for ir in range(-r,r+1):
        ij = set([abs(ir)-r,r-abs(ir)]) if hollow == True else [jx for jx in range(abs(ir)-r,r-abs(ir)+1)]
        for jr in ij:
            locs.append([i+ir,j+jr])
    locs = sorted(locs)
    return locs

# distance matrix
def dist_matrix(dim=8,cost=1):
    dm = np.zeros((dim,dim))
    for i in range(dim):
        bin_i = int2arr(i,3)
        for j in range(dim):
            bin_j = int2arr(j,3)
            dij = np.sum([abs(bi-bj) for bi,bj in zip(bin_i,bin_j)])
            dm[i][j] = cost * dij
    return dm

# convert ring world > ring environment > int
def env2int(world,i=None,j=None):
    # if not centered
    i = int(world.shape[0]/2) if not i else i
    j = int(world.shape[1]/2) if not j else j
    # assuming ring of 4 elements
    env = world[i-2:i+3,j-2:j+3].flatten()
    for dx in [24,20,17,13,12,11,7,4,0]:
        env = np.delete(env,dx)
    xi = arr2int(env)
    return xi

# only for ring envs (16 elements)
def int2ring_env(xi,unknown=0):
    env = int2arr(xi,arr_len=16)
    for di in [0,4,7,11,12,13,17,20,24]:
        env = np.insert(env,di,unknown)
    env = env.reshape(5,5)
    return env

# gol timestep (bounded domains)
def gol_timestep(domain):
    # only int 0/1
    dcopy = domain.astype(int)
    # iterate through cells
    for ei,di in enumerate(domain):
        for ej,dij in enumerate(di):
            # apply gol rule (max for borders)
            nbsum = np.sum(domain[max(0,ei-1):ei+2,max(0,ej-1):ej+2]) - dij
            dcopy[ei,ej] = 1 if nbsum==3 or (nbsum==2 & dij==1) else 0
    return dcopy

# tx matrix for a GoL individual cell
def txs_gol_cell():
    # 512 txs, 2 sts (sti,stx) & 9 cells domain
    tx_tensor = np.zeros((512,2,9))
    tx_matrix = np.zeros((512,512))
    # for each sti 0:512 -> stx
    for i in range(512):
        # sti
        sti = int2arr(i,arr_len=9)
        tx_tensor[i,0] = sti
        # stx
        stx = gol_timestep(sti.reshape(3,3))
        tx_tensor[i,1] = stx.flatten()
        # sti -> stx
        x = arr2int(stx)
        tx_matrix[i,x] += 1
    return tx_tensor,tx_matrix



         # for me,mx in enumerate(self.mxs[cfg]):
            #     # elementary purviews
            #     a0,a1 = self.fpws[cfg][0]
            #     b0,b1 = self.fpws[cfg][1]
            #     c0,c1 = self.fpws[cfg][2]
            #     d0,d1 = self.fpws[cfg][3]
            #     e0,e1 = self.fpws[cfg][4]
            #     # likelihood of fut values for pw=0 and pw=1
            #     fa = np.sum(self.tm*a0)*a0 + np.sum(self.tm*a1)*a1
            #     fb = np.sum(self.tm*b0)*b0 + np.sum(self.tm*b1)*b1
            #     fc = np.sum(self.tm*c0)*c0 + np.sum(self.tm*c1)*c1
            #     fd = np.sum(self.tm*d0)*d0 + np.sum(self.tm*d1)*d1
            #     fe = np.sum(self.tm*e0)*e0 + np.sum(self.tm*e1)*e1
            #     # valid fut values for pws, given that mx = 1 = current pw
            #     m1 = np.sum(self.tm * mx.T,axis=0)
            #     mxa = np.sum(m1*a0)*a0 + np.sum(m1*a1)*a1
            #     mxb = np.sum(m1*b0)*b0 + np.sum(m1*b1)*b1
            #     mxc = np.sum(m1*c0)*c0 + np.sum(m1*c1)*c1
            #     mxd = np.sum(m1*d0)*d0 + np.sum(m1*d1)*d1
            #     mxe = np.sum(m1*e0)*e0 + np.sum(m1*e1)*e1
            #     # elementary pws fut values, given mechanism mx = 1
            #     self.exs[cfg,me,0] = mxa * fb*fc*fd*fe
            #     self.exs[cfg,me,1] = fa* mxb *fc*fd*fe
            #     self.exs[cfg,me,2] = fa*fb* mxc *fd*fe
            #     self.exs[cfg,me,3] = fa*fb*fc* mxd *fe
            #     self.exs[cfg,me,4] = fa*fb*fc*fd * mxe

        # self.lx_ppws,self.lx_fpws = [],[]
        # pp1 = self.sts[:,0,1:-1,1:-1].reshape(16,9).T
        # pps = [np.abs(pp1-1),pp1]
        # fp1 = self.sts[:,2,1:-1,1:-1].reshape(16,9).T
        # fps = [np.abs(fp1-1),fp1]
        # # until i find a better way to do this
        # for cfg in range(16):
        #     ppws,fpws = [],[]
        #     cfg_pws = self.sts[cfg,1,1:-1,1:-1].nonzero()[0]
        #     # first order
        #     for pi in cfg_pws:
        #         ppws.append([pps[0][pi],pps[1][pi]])
        #         fpws.append([fps[0][pi],fps[1][pi]])
        #     # second order
        #     for a,b in list(combinations(cfg_pws,2)):
        #         ppws.append([pps[0][a]*pps[0][b],pps[0][a]*pps[1][b],pps[1][a]*pps[0][b],pps[1][a]*pps[1][b]])
        #         fpws.append([fps[0][a]*fps[0][b],fps[0][a]*fps[1][b],fps[1][a]*fps[0][b],fps[1][a]*fps[1][b]])
        #     # third order
        #     for a,b,c in list(combinations(cfg_pws,3)):
        #         p3p,p3f = [],[]
        #         for u in range(8):
        #             i,j,k = int2arr(u,3)
        #             p3p.extend([pps[i][a]*pps[j][b]*pps[k][c]])
        #             p3f.extend([fps[i][a]*fps[j][b]*fps[k][c]])
        #         ppws.append(p3p)
        #         fpws.append(p3f)
        #     # 4th order
        #     for a,b,c,d in list(combinations(cfg_pws,4)):
        #         p4p,p4f = [],[]
        #         for u in range(16):
        #             i,j,k,l = int2arr(u,4)
        #             p4p.extend([pps[i][a]*pps[j][b]*pps[k][c]*pps[l][d]])
        #             p4f.extend([fps[i][a]*fps[j][b]*fps[k][c]*fps[l][d]])
        #         ppws.append(p4p)
        #         fpws.append(p4f)
        #     # system pw
        #     #
        #     # easier using tm
        #     self.lx_ppws.append(ppws)
        #     self.lx_fpws.append(fpws)
        # import pdb; pdb.set_trace()

    # def glst(self):
        # simple return glider st as 2d rep & active cells indices
        # return self.sts[self.st,1],self.sts[self.st,1,1:-1,1:-1].flatten().nonzero()[0]

    # def mk_reps(self):
        # # causes
        # for cfg in range(16):
        #     # everything works using matmul, but sum,axis for causal clarity
        #     for me,mx in enumerate(self.mxs[cfg]):
        #         # valid past gl cfgs leading to current mx=1
        #         glp_mx = np.sum(self.tm*mx,axis=1)
        #         # for each purview
        #         for pwi,pwx in enumerate(self.lx_ppws[cfg][:-1]):
        #             # past pws vals leading to current cfg, where: mx = c pws = 1
        #             self.cxs[cfg,me,pwi] = np.sum(np.sum(glp_mx*pwx,axis=1).reshape(len(pwx),1)*pwx,axis=0)
        #         # system purview
        #         self.cxs[cfg,me,30] = np.sum(self.cxs[cfg,me,:5],axis=0)
        #         # as distributions
        #         mx_sums = np.sum(self.cxs[cfg,me],axis=1)
        #         mx_sums = np.where(mx_sums==0,1,0).reshape(31,1)
        #         self.cxs[cfg,me] = self.cxs[cfg,me]/mx_sums
        # import pdb; pdb.set_trace()
        # effects

        # fut values for a=0 and a=1 (pws without mechanisms yet)
        # fa = np.sum(self.tm*self.a0)*self.a0 + np.sum(self.tm*self.a1)*self.a1
        # fb = np.sum(self.tm*self.b0)*self.b0 + np.sum(self.tm*self.b1)*self.b1
        # fc = np.sum(self.tm*self.c0)*self.c0 + np.sum(self.tm*self.c1)*self.c1
        # mechanisms
        # m1 = np.sum(self.tm * self.a1.T,axis=0)
        # mx1 = np.sum(m1*self.a0)*self.a0 + np.sum(m1*self.a1)*self.a1
        # cxa1 = mx1 * fb * fc

        # # first order causes
        # for cfg in range(16):
        #     # active cells forming the glider
        #     ces = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
        #     # for every purview
        #     for pwi in range(1,32):
        #         pwx = ces*self.pws[pwi]
        #         # for each single mechanism
        #         for e,ce in enumerate(ces):
        #             # values for the cxs reps indexes
        #             cis = np.zeros(5).astype(int)
        #             cis[e] = 1
        #             c0,c1,c2,c3,c4 = cis
        #             # glider pasts that could have led to cell = 1
        #             # valid txs in which cell stx == 1 (mechanism)
        #             # gps = np.sum(self.tm*self.cvw[ce,1],axis=1)
        #             gps = np.matmul(self.tm,self.cvw[ce,1])
        #             # active cells in current purview
        #             # info from past st shouldn't be very good (due to the transient cfgs)?
        #             pwu = pwx[~np.isnan(pwx)].astype(int)
        #             cps = (self.sts[cfg,1]*np.sum([self.ces_pws[pw] for pw in pwu],axis=0))[1:-1,1:-1].flatten().nonzero()[0]
        #             # all gl states where cells in purview are active
        #             cps_gl = np.array([self.cvw[cpi,1] for cpi in cps])
        #             cps_gl = np.pad(cps_gl,(0,5),'constant')[:5,:16]
        #             # only valid glider pasts, leading to cell = 1
        #             # possible gl past sts where pp cells were active
        #             # => number of valid past gl sts where each pp cell past st = 1
        #             # cps_pp = np.sum(cps_cfgs*gps,axis=1)
        #             cps_pp = np.matmul(cps_gl,gps)
        #             # for every gl cfg, the sum of the possibilities of all pp cells
        #             self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = np.matmul(cps_gl.T,cps_pp)
        #         # higher order mechanisms
        #         mxs = np.where(np.isnan(self.pws),0,1)
        #         for mi in range(1,32):
        #             if np.sum(mxs[mi])>0:
        #                 # avoid conflicting with already gotten first order mxs
        #                 cx = np.ones(16)
        #                 c0,c1,c2,c3,c4 = mxs[mi].astype(int)
        #                 if c0==1:
        #                     cx *= self.cxs[cfg,pwi,c0,0,0,0,0]
        #                 if c1==1:
        #                     cx *= self.cxs[cfg,pwi,0,c1,0,0,0]
        #                 if c2==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,c2,0,0]
        #                 if c3==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,0,c3,0]
        #                 if c4==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,0,0,c4]
        #                 self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = cx
        #
















#
