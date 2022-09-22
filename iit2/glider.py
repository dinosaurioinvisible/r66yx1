
import numpy as np
from aux import *
from pyemd import emd

'''
There are 6 options for measuring phi, that i can think of:
1. system made of 1s (only 1s can be infomative)
2. considering past/fut 0s as informative as well
3. broadened pws, considering a 3x3 pw for each cell
4. system as organization, so of 7 (2->0,3=1,2->1) elements
5. system as the lattice, including 0s and 1s
6. retrotxs, so that info comes from change, not from sts
'''

'''
there are 3 options for constructing the purviews:
1. (A)(B)CDE: considering past cfg (but where would this info come from?)
2. ()()CDE()(): considering only elements in past & present (but FG are there!)
3. ()()CDEFG: considering present cfg and look into the past
so then, taking opt3, we could:
2a. consider only 1s as informative (but this would lead to opt2)
2b. consider 0s as informative as well, of destruction and creation
=> info from past/fut cfgs where A=0 or 1, given that current mxA = pwA = 1
so for every cfg there is info about what it was not there (from FG),
but still there is a loss of complete information (AB)
'''

class Glider:
    def __init__(self):
        # current st
        self.st = 0
        # glider past,current,future sts for all canonical cfgs
        self.sts = np.zeros((16,3,5,5))
        # indices for active cells for every cfg (for analysis)
        self.ids = np.zeros((16,5)).astype(int)
        # transition matrix in empty env
        self.tm = np.zeros((16,16)).astype(int)
        self.mk_glider()
        # active mechanisms vals for every cfg, given current gl cfg (cfg,mxs,vals)
        self.mxs = np.zeros((16,31,16))
        self.mk_mxs()
        # cell 1/0 vals in past & fut (from current cfg pov)
        self.ppws = np.zeros((16,5,16))
        self.fpws = np.zeros((16,5,16))
        self.mk_pws()
        # cause and effect repertoires (cfgs,mxs,pws,dists)
        self.cxs = np.zeros((16,31,31,16))
        self.mk_cxs()
        self.exs = np.zeros((16,31,31,16))
        # unconstrained futures for every cfg
        self.ucf = np.zeros((16,16))
        self.mk_exs()
        # small phi: intrinsic information (cfg,mx,pw info)
        self.cxinfo = np.zeros((16,31,31))
        self.exinfo = np.zeros((16,31,31))
        self.info = np.zeros((16,31))
        self.get_info()
        # analysis
        self.analyze()

    def mk_glider(self):
        # glider base sts (SE)
        gi = np.array([[0,0,1],[1,0,1],[0,1,1]])
        gx = np.array([[1,0,0],[0,1,1],[1,1,0]])
        # gl sts: r = 0:SE, 1:NE, 2:NW, 3:SW
        for r in range(4):
            self.sts[4*r+0,1,1:-1,1:-1] = np.rot90(gi,r)
            self.sts[4*r+1,1,1:-1,1:-1] = np.rot90(gx,r)
            self.sts[4*r+2,1,1:-1,1:-1] = np.rot90(np.transpose(gi),r)
            self.sts[4*r+3,1,1:-1,1:-1] = np.rot90(np.transpose(gx),r)
            # past=0 and future=2 sts
            self.sts[4*r:4*(r+1),0] = np.roll(self.sts[4*r:4*(r+1),1],1,axis=0)
            self.sts[4*r:4*(r+1),2] = np.roll(self.sts[4*r:4*(r+1),1],-1,axis=0)
            # txs, only for the empty case
            self.tm[4*r:4*(r+1),4*r:4*(r+1)] = np.roll(np.diag((1,1,1,1)),1,axis=1)
        # override past/future sts where there is translation
        for cfg in [0,6,8,14]:
            # horizontal
            dj = 1 if cfg in [0,6] else -1
            self.sts[cfg,2] = np.roll(self.sts[cfg,2],dj,axis=1)
            self.sts[cfg+1,0] = np.roll(self.sts[cfg+1,0],-dj,axis=1)
        # current (t) -> future <=> past <- current (t+1)
        for cfg in [2,4,10,12]:
            # vertical
            di = 1 if cfg in [2,12] else -1
            self.sts[cfg,2] = np.roll(self.sts[cfg,2],di,axis=0)
            self.sts[cfg+1,0] = np.roll(self.sts[cfg+1,0],-di,axis=0)

    def mk_mxs(self):
        # make mechanisms
        # for composition of higher order subsys (AB,ABC,ABCD,etc) (31, omitting all zeroes)
        mx_subsys = powerset(5,min_set_size=2)
        # first order mechanisms (active cells)
        ### (this could be also made by taking indices only, and building all 512 subsys once)
        for cfg in range(16):
            # active cells (5), acting as causal elementary mechanisms for given cfg
            ### (in an empty space, all cells=0 become part of the env(?))
            self.ids[cfg] = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # gl cfgs where these cells are active (i.e. mechanisms) from the 16 cfgs
            self.mxs[cfg,:5] = self.sts[:,1,1:-1,1:-1].reshape(16,9).T[self.ids[cfg]]
            # higher order mechanisms
            for me,mx in enumerate(mx_subsys):
                # all combinations of the (5) 1st order mechanisms
                self.mxs[cfg,me+5] = np.product(self.mxs[cfg][np.asarray(mx)],axis=0)

    '''this yields strangely high values of information,
    specially for the elementary effects'''
    def mk_pws_motion(self):
        # make purviews
        # cfgs as future and past from other cgfs (considering production/motion)
        ### (this is to avoid ill references/comparisons like c0==c1)
        self.as_fsts = np.zeros((16,5,5))
        for cfg in range(16):
            # following the transition matrix
            fst = self.tm[:,cfg].nonzero()[0]
            # get current cfg's fut from the cfg which future is current cfg
            self.as_fsts[cfg] = self.sts[fst,2]
        # pasts are the pasts of every next cfg in self.sts
        self.as_psts = np.roll(self.sts[:,0],-1,axis=0)
        # past/fut elementary purviews
        for cfg in range(16):
            # current active cells (elementary purviews)
            cfg_pws = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # for every active cell in current cfg, all cfgs vals 0/1
            self.fpws[cfg] = self.as_fsts[:,1:-1,1:-1].reshape(16,9).T[cfg_pws]
            self.ppws[cfg] = self.as_psts[:,1:-1,1:-1].reshape(16,9).T[cfg_pws]

    def mk_pws_direct(self):
        # make purviews, simpler version
        # pasts and futures cfg of every cfg
        ppws = self.sts[:,0,1:-1,1:-1].reshape(16,9).T
        fpws = self.sts[:,2,1:-1,1:-1].reshape(16,9).T
        # for every cfg
        for cfg in range(16):
            # active cells (i.e. that can act as pws) for current cfg
            cfg_pws = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            self.ppws[cfg] = ppws[cfg_pws]
            self.fpws[cfg] = fpws[cfg_pws]

    def mk_pws(self):
        for cfg in range(16):
            # active cells (i.e. that can act as pws) for current cfg and past or future
            ppws_ids = (self.sts[cfg,0]*self.sts[cfg,1])[1:-1,1:-1].flatten().nonzero()[0]
            fpws_ids = (self.sts[cfg,1]*self.sts[cfg,2])[1:-1,1:-1].flatten().nonzero()[0]
            # elementary purviews (should be 3 for each)
            self.ppws[cfg,:ppws_ids.shape[0]] = self.sts[:,0,1:-1,1:-1].reshape(16,9).T[ppws_ids]
            self.fpws[cfg,:fpws_ids.shape[0]] = self.sts[:,2,1:-1,1:-1].reshape(16,9).T[fpws_ids]

    def mk_cxs(self):
        # for higher order combinations of purviews
        pws2 = powerset(5,min_set_size=2,max_set_size=2)
        pws3 = powerset(5,min_set_size=3,max_set_size=3)
        pws4 = powerset(5,min_set_size=4,max_set_size=4)
        # for causes, for each mx we need all pws
        # AB/BC=00 => AB/B=0 * AB/C=0 (mxs can be multiplied)
        for cfg in range(16):
            # all can be done with matmul, but i prefer sum,axis for clarity
            # i could've multiplied the higher order mxs, but it was as expensive as this
            for me,mx in enumerate(self.mxs[cfg]):
                # past gl cfgs that could have led to mx=1
                psmx = np.sum(self.tm*mx,axis=1)
                # cxs from elementary purviews for mx
                self.cxs[cfg,me,:5] = np.sum(self.ppws[cfg]*psmx,axis=1).reshape(5,1)*self.ppws[cfg] + np.sum(np.abs(self.ppws[cfg]-1)*psmx,axis=1).reshape(5,1)*np.abs(self.ppws[cfg]-1)
                # second order pws (10)
                for pwe,pwi in enumerate(pws2):
                    # for every subsystem of 2 elements
                    ab = self.ppws[cfg][np.asarray(pwi)]
                    # a1b1, b1a0, a0b0, b0a1
                    pwx = np.vstack((ab,np.abs(ab-1))) * np.roll(np.vstack((ab,np.abs(ab-1))),-1,axis=0)
                    self.cxs[cfg,me,5+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(4,1)*pwx,axis=0)
                # third order pws (10)
                for pwe,pwi in enumerate(pws3):
                    # for each subsystem of 3 elements
                    a,b,c = self.ppws[cfg][np.asarray(pwi)]
                    # a0x4,a1x4 * b0x2,b1x2;x2 * c0c1;x4
                    pwx = np.repeat([np.abs(a-1),a],[4,4],axis=0) * np.tile([np.abs(b-1),b],(2,2)).reshape(8,16) * np.tile([np.abs(c-1),c],(4,1))
                    self.cxs[cfg,me,15+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(8,1)*pwx,axis=0)
                # fourth order (5)
                for pwe,pwi in enumerate(pws4):
                    # for each subsystem of 4 elements
                    a,b,c,d = self.ppws[cfg][np.asarray(pwi)]
                    # same, but a0x8,a1x8, etc
                    pwx = np.repeat([np.abs(a-1),a],[8,8],axis=0) * np.tile([np.abs(b-1),b],(2,4)).reshape(16,16) * np.tile([np.abs(c-1),c],(4,2)).reshape(16,16) * np.tile([np.abs(d-1),d],(8,1))
                    self.cxs[cfg,me,25+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(16,1)*pwx,axis=0)
                # all elements together (whole system) (1)
                a,b,c,d,e = self.ppws[cfg]
                pwx = np.repeat([np.abs(a-1),a],[16,16],axis=0) * np.tile([np.abs(b-1),b],(2,8)).reshape(32,16) * np.tile([np.abs(c-1),c],(4,4)).reshape(32,16) * np.tile([np.abs(d-1),d],(8,2)).reshape(32,16) * np.tile([np.abs(e-1),e],(16,1))
                self.cxs[cfg,me,30] = np.sum(np.sum(pwx*psmx,axis=1).reshape(32,1)*pwx,axis=0)
                # turn counts into distributions
                self.cxs[cfg,me] /= np.sum(self.cxs[cfg,me],axis=1).reshape(31,1)

    def mk_exs(self):
        # purviews powerset, for higher order purviews
        pwset = powerset(5,min_set_size=2)
        # effects prob. distributions
        # for effects: ABC/AB=10 => A/AB=10 * B/AB=10 * C/AB=10
        # purviews can be multiplied, for the same mechanisms
        for cfg in range(16):
            # elementary pws (5) future cfgs where fpw = 1
            # a1,b1,c1,d1,e1 = [fpwi.reshape(1,16) for fpwi in self.fpws[cfg]]
            # effect matrices, including virtual uc elements
            # likelihood of fut pws vals =0 or =1
            tma,tmb,tmc,tmd,tme = [np.sum(self.tm*np.abs(pwi-1),axis=1).reshape(16,1)*np.abs(pwi-1)+np.sum(self.tm*pwi,axis=1).reshape(16,1)*pwi for pwi in self.fpws[cfg]]
            # unconstrained future pws
            ufa,ufb,ufc,ufd,ufe = [np.sum(tm,axis=0) for tm in [tma,tmb,tmc,tmd,tme]]
            # elementary purviews for every mechanism
            for me,mx in enumerate(self.mxs[cfg]):
                # elementary pws fut vals, given mx=1
                self.exs[cfg,me,0] = np.sum(tma*mx.reshape(16,1),axis=0) * ufb*ufc*ufd*ufe
                self.exs[cfg,me,1] = ufa* np.sum(tmb*mx.reshape(16,1),axis=0) *ufc*ufd*ufe
                self.exs[cfg,me,2] = ufa*ufb* np.sum(tmc*mx.reshape(16,1),axis=0) *ufd*ufe
                self.exs[cfg,me,3] = ufa*ufb*ufc* np.sum(tmd*mx.reshape(16,1),axis=0) *ufe
                self.exs[cfg,me,4] = ufa*ufb*ufc*ufd * np.sum(tme*mx.reshape(16,1),axis=0)
                # higher order purviews
                for pwi,pwx in enumerate(pwset):
                    self.exs[cfg,me,5+pwi] = np.product(self.exs[cfg,me][np.asarray(pwx)],axis=0)
                # turn mx counts into distributions
                self.exs[cfg,me] /= np.sum(self.exs[cfg,me],axis=1).reshape(31,1)
            # uncontrained future (different for every cfg)
            ucf = ufa*ufb*ufc*ufd*ufe
            self.ucf[cfg] = ucf/np.sum(ucf)

    def get_info(self):
        # distance matrix, uc past (homogeneous for all)
        dm = mk_dm(16)
        ucp = np.ones(16)/16
        # for every cfg, mechanism and purview
        for cfg in range(16):
            for me in range(31):
                for pwi in range(31):
                    # compare with unconstrained past and future
                    self.cxinfo[cfg,me,pwi] = emd(self.cxs[cfg,me,pwi],ucp,dm)
                    self.exinfo[cfg,me,pwi] = emd(self.exs[cfg,me,pwi],self.ucf[cfg],dm)
                # intrinsic info: minimum between causes and effects
                self.info[cfg,me] = np.min((np.max(self.cxinfo[cfg,me]),np.max(self.exinfo[cfg,me])))

    def analyze(self):
        # combinations (subsystems) of mechanisms
        pset = powerset(5)
        # max intrinsic info (present from past & future)
        self.maxinfo = np.zeros(16)
        self.maxinfo_ids = []
        self.maxinfo_sxe = np.zeros(16)
        # synergy: current sys info of past, present & fut
        # (16 cfgs, 3 timeframes: 0:p/c, 1:c/ii(p,f), 2:f/c)
        # em/em, em/sys, diff
        # self.synems = np.zeros((16,3,5,3))
        # (sys/em,sys/ems,sum(ems)/sys) - diff (with sys/sys)
        self.synsys = np.zeros((16,3,7,2))
        # different for every cfg
        for cfg in range(16):
            # IIT
            # max informative mechanism
            maxinfo = np.max(self.info[cfg])
            self.maxinfo[cfg] = maxinfo
            # all mechanisms/subsystems providing max info
            maxids = np.where(self.info[cfg]==maxinfo)[0]
            self.maxinfo_ids.append([self.ids[cfg][np.asarray(pset[mid])] for mid in maxids])
            # system info versus the sum of all elementary mxs info
            # (this shouldn't be useful, due to purview mismatch (sys/sys? <> elems/elems?), but just in case)
            self.maxinfo_sxe[cfg] = self.info[cfg][30] - np.sum(self.info[cfg,:5])
        # synergies (1:present, 0:past, 2:future)
        # past
        self.synsys[:,0,:,0] = np.hstack((self.cxinfo[:,30,:5],self.cxinfo[:,30,30].reshape(16,1),np.sum(self.cxinfo[:,30,:5],axis=1).reshape(16,1)))
        self.synsys[:,0,:,1] = np.tile(self.cxinfo[:,30,30],(7,1)).T - self.synsys[:,0,:,0]
        # future
        self.synsys[:,2,:,0] = np.hstack((self.exinfo[:,30,:5],self.exinfo[:,30,30].reshape(16,1),np.sum(self.exinfo[:,30,:5],axis=1).reshape(16,1)))
        self.synsys[:,2,:,1] = np.tile(self.exinfo[:,30,30],(7,1)).T - self.synsys[:,2,:,0]
        # present (for sys/sum(ems) we need to add the mins from past & fut)
        self.synsys[:,1,:,0] = np.minimum(self.synsys[:,0,:,0],self.synsys[:,2,:,0])
        self.synsys[:,1,6,0] = np.sum(self.synsys[:,1,:5,0],axis=1)
        self.synsys[:,1,:,1] = np.tile(np.minimum(self.cxinfo[:,30,30],self.exinfo[:,30,30]),(7,1)).T - self.synsys[:,1,:,0]

        # print some stuff
        print('\nmax info, sxe?, subsys[minsize & common elements]:\n')
        minsets = [set.intersection(*[set(list(mi)) for mi in self.maxinfo_ids[i]]) for i in range(16)]
        info_sets = [[len(self.maxinfo_ids[i][0]),minsets[i]] for i in range(16)]
        for i in [[a,b,c] for a,b,c in zip(self.maxinfo,self.maxinfo_sxe,info_sets)]:
            print(' {:.2f}, {:.2f}, {}'.format(i[0],i[1],i[2]))
        print('\nsystem synergy: past,present,future: sys|sys-sys|sum(ems)\n')
        print(self.synsys[:,:,6,1])
        print('\npast synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,0]>0)[0]))
        print('present synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,1]>0)[0]))
        print('future synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,2]>0)[0]))










































#
