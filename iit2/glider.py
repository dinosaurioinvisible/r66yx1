
import numpy as np
from aux import *
from pyemd import emd
import xlsxwriter

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
    def __init__(self,current_tf_only=False,write_to_xlsx=False):
        # opt
        self.ctf = current_tf_only
        self.write = write_to_xlsx
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
        self.info = np.zeros((16,31,31))
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
        # just to align the transitions -> 0:sE, 1:nE, 2:nW, 3:sW
        # when i have time im changing all this part
        self.sts[4:8] = np.roll(self.sts[4:8],2,axis=0)
        self.sts[12:] = np.roll(self.sts[12:],2,axis=0)

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

    def mk_pws_direct(self):
        # make purviews, simplest version (for comparison only)
        pws = self.sts[:,1,1:-1,1:-1].reshape(16,9).T
        # for every cfg
        for cfg in range(16):
            # active cells (i.e. that can act as pws) for current cfg
            cfg_pws = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # domain to domain purviews
            self.ppws[cfg] = self.fpws[cfg] = pws[cfg_pws]

    def mk_pws_binary(self,current_tf=True):
        # this should work well for binary wholy known systems, not the case
        for cfg in range(16):
            # active cells ids in current time frame
            pws_ids = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # past and future pws (for active ids)
            self.ppws[cfg] = self.sts[:,0,1:-1,1:-1].reshape(16,9).T[pws_ids]
            self.fpws[cfg] = self.sts[:,2,1:-1,1:-1].reshape(16,9).T[pws_ids]
            # for elementary purviews
            if current_tf:
                # indices where current cells were also active in the past/fut
                ppws = [1 if pi in self.sts[cfg,0,1:-1,1:-1].flatten().nonzero()[0] else 0 for pi in pws_ids]
                fpws = [1 if pi in self.sts[cfg,2,1:-1,1:-1].flatten().nonzero()[0] else 0 for pi in pws_ids]
                # consider only cells present in both time frames
                self.ppws[cfg] = self.ppws[cfg] * np.asarray(ppws).reshape(5,1)
                self.fpws[cfg] = self.fpws[cfg] * np.asarray(fpws).reshape(5,1)

    def mk_pws(self):
        # for distance matrices
        self.pdm = np.zeros((16,16))
        self.fdm = np.zeros((16,16))
        # elementary past/fut 3x3 purviews considering 'motion'
        ppws = self.sts[:,0,1:-1,1:-1].reshape(16,9).T
        # indices for future pws from tx matrix
        # fpw of cfg=0 as fut of cfg=3 and so on
        fut_ids = self.tm.T.nonzero()[1]
        # 0/1 for every cell, for every glider cfg
        fpws = self.sts[fut_ids,2,1:-1,1:-1].reshape(16,9).T
        for cfg in range(16):
            # indices for alive cells in current cfg
            pws_ids = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # past/future pws taken from each cfg's displaced past/future
            self.ppws[cfg] = ppws[pws_ids]
            self.fpws[cfg] = fpws[pws_ids]
            # if we wish to include only cells 'connecting' time-frames
            if self.ctf:
                # indices for connecting cells (alive in both timeframes)
                pc_pws = [1 if pi in self.sts[cfg,0,1:-1,1:-1].flatten().nonzero()[0] else 0 for pi in pws_ids]
                cf_pws = [1 if pi in self.sts[cfg,2,1:-1,1:-1].flatten().nonzero()[0] else 0 for pi in pws_ids]
                # nonsystem cells are excluded (pw=0)
                self.ppws[cfg] *= np.asarray(pc_pws).reshape(5,1)
                self.fpws[cfg] *= np.asarray(cf_pws).reshape(5,1)
            # make a distance matrix (limited to known sts, not fully binary)
            # 5 (max cost) - connecting cells between sts
            self.pdm[cfg] = 5 - np.sum(ppws.T*self.sts[cfg,1,1:-1,1:-1].flatten(),axis=1)
            self.fdm[cfg] = 5 - np.sum(fpws.T*self.sts[cfg,1,1:-1,1:-1].flatten(),axis=1)
        # just checking (it seems that self elementary info = 0?)
        self.pdm *= np.abs(1-np.diag(np.ones(16)))
        self.fdm *= np.abs(1-np.diag(np.ones(16)))

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
            # effect matrices, including virtual uc elements
            # likelihood of fut pws vals =0 or =1
            # this is a kind of roundabout, but its easier to visualize
            tms = [np.sum(self.tm*np.abs(pwi-1),axis=1).reshape(16,1)*np.abs(pwi-1)+np.sum(self.tm*pwi,axis=1).reshape(16,1)*pwi for pwi in self.fpws[cfg]]
            # unconstrained future pws
            ufs = np.array([np.sum(tm,axis=0) for tm in tms])
            # elementary purviews for every mechanism
            for me,mx in enumerate(self.mxs[cfg]):
                # elementary pws fut vals, given mx=1
                for pwe in range(5):
                    # only non considered pws are unconstrained
                    ufx = ufs*1
                    ufx[pwe] = 1
                    ufx = np.product(ufx,axis=0)
                    self.exs[cfg,me,pwe] = np.sum(tms[pwe]*mx.reshape(16,1),axis=0) * ufx
                # higher order purviews
                for pwi,pwx in enumerate(pwset):
                    ufx = ufs*1
                    ufx[np.asarray(pwx)] = 1
                    ufx = np.product(ufx,axis=0)
                    # self.exs[cfg,me,5+pwi] = np.product(self.exs[cfg,me][np.asarray(pwx)],axis=0) * ufx
                    px = np.array([np.sum(tms[pi]*mx.reshape(16,1),axis=0) for pi in pwx])
                    self.exs[cfg,me,5+pwi] = np.product(px,axis=0) * ufx
                # turn mx counts into distributions
                self.exs[cfg,me] /= np.sum(self.exs[cfg,me],axis=1).reshape(31,1)
            # uncontrained future (different for every cfg)
            ucf = np.product(ufs,axis=0)
            self.ucf[cfg] = ucf/np.sum(ucf)

    def get_info(self):
        # distance matrix, uc past (homogeneous for all)
        # dm = mk_dm(16)
        ucp = np.ones(16)/16
        # for every cfg, mechanism and purview
        for cfg in range(16):
            for me in range(31):
                for pwi in range(31):
                    # compare with unconstrained past and future
                    self.cxinfo[cfg,me,pwi] = emd(self.cxs[cfg,me,pwi],ucp,self.pdm)
                    self.exinfo[cfg,me,pwi] = emd(self.exs[cfg,me,pwi],self.ucf[cfg],self.fdm)
                # intrinsic info: minimum between causes and effects
                self.info[cfg,me] = np.minimum(self.cxinfo[cfg,me],self.exinfo[cfg,me])

    def analyze(self):
        # combinations (subsystems) of mechanisms
        pset = powerset(5)
        # max intrinsic info (present from past & future)
        self.maxinfo = np.zeros(16)
        self.maxinfo_ids = []
        # synergy: current sys info of past, present & fut
        # (16 cfgs, 3 timeframes: 0:p/c, 1:c/ii(p,f), 2:f/c)
        # (sys/em, sys/sys, sys/sys-sum(ems)/sys)
        self.synsys = np.zeros((16,3,7,2))
        # different for every cfg
        for cfg in range(16):
            # max informative purview for each mechanism
            max_pws = np.max(self.info[cfg],axis=1)
            # max informatie mechanism for each cfg
            max_mx = np.max(max_pws)
            self.maxinfo[cfg] = max_mx
            # all mechanisms/subsystems providing max info
            max_ids = np.where(max_pws==max_mx)[0]
            self.maxinfo_ids.append([self.ids[cfg][np.asarray(pset[mid])] for mid in max_ids])

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
        print('\nmax info, sys info, elms info, subsys[minsize & common elms]:\n')
        minsets = [set.intersection(*[set(list(mi)) for mi in self.maxinfo_ids[i]]) for i in range(16)]
        info_sets = [[len(self.maxinfo_ids[i][0]),minsets[i]] for i in range(16)]
        for i in [[a,b,c,d] for a,b,c,d in zip(self.maxinfo,self.info[:,30,30],np.sum(self.info[:,:5,30],axis=1),info_sets)]:
            print(' {:.2f}, {:.2f}, {:.2f}, {}'.format(i[0],i[1],i[2],i[3]))
        print('\nsystem synergy: past,present,future: sys|sys-sys|sum(ems)\n')
        print(np.round(self.synsys[:,:,6,1],2))
        print('\npast synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,0]>0)[0]))
        print('present synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,1]>0)[0]))
        print('future synergies: {}'.format(np.where(self.synsys[:,:,6,1][:,2]>0)[0]))

        # synergies2 (the other way around)
        print("\nsynergyes:\n")
        print('   psum, psys,psyn - csyn - fsyn,fsys, fsum')
        psum = np.sum(self.cxinfo[:,:5,30],axis=1).reshape(16,1)
        psys = self.cxinfo[:,30,30].reshape(16,1)
        psyn = np.diff(np.hstack((np.sum(self.cxinfo[:,:5,30],axis=1).reshape(16,1),self.cxinfo[:,30,30].reshape(16,1))),axis=1)
        csyn = self.info[:,30,30] - np.sum(self.info[:,:5,30],axis=1)
        fsyn = np.diff(np.hstack((np.sum(self.exinfo[:,:5,30],axis=1).reshape(16,1),self.exinfo[:,30,30].reshape(16,1))),axis=1)
        fsys = self.exinfo[:,30,30].reshape(16,1)
        fsum = np.sum(self.exinfo[:,:5,30],axis=1).reshape(16,1)
        print(np.round(np.hstack((psum,psys,psyn,csyn.reshape(16,1),fsyn,fsys,fsum)),2))

        print('\ncurrent timeframe synergy')
        print(np.round(np.vstack((np.sum(self.info[:,:5,30],axis=1),self.info[:,30,30],csyn)).T,2))

        if self.write:
            # names od the elements
            pset = powerset(5)[1:]
            # initialize worksheet
            workbook = xlsxwriter.Workbook('glxinfo.xlsx')
            worksheet = workbook.add_worksheet()
            row,col = 2,1
            worksheet.write(row,col, 'phi')
            # for every config
            for cfgi,cfgx in enumerate(self.info):
                wx = 'cfg = {}'.format(cfgi)
                worksheet.write(row,col, wx)
                # upper names
                for pwi in range(30):
                    worksheet.write(row,col+pwi+1, '{}'.format(pset[pwi]))
                # left names and data
                for mxi in range(30):
                    row += 1
                    worksheet.write(row,col, '{}'.format(pset[mxi]))
                    for pwi in range(30):
                        worksheet.write(row,col+pwi+1, cfgx[mxi,pwi])
                # for next config
                row += 2
            workbook.close()

        # 16 cfgs -> A and B
        ab_info = False
        if ab_info:
            ab = self.info[:,:5,30]
            absum = np.round(np.sum(self.info[:,:5,30],axis=1),2)
            ems = ['A','B','C','D','E','SUM']
            workbook = xlsxwriter.Workbook('glxAB.xlsx')
            worksheet = workbook.add_worksheet()
            row,col = 2,1
            worksheet.write(row,col, 'phi')
            for pwi in range(len(ems)):
                worksheet.write(row,col+pwi+1, '{}'.format(ems[pwi]))
            for cfg in range(16):
                row += 1
                worksheet.write(row,col, 'cfg={}'.format(cfg))
                for pwi in range(5):
                    worksheet.write(row,col+pwi+1, ab[cfg,pwi])
                worksheet.write(row,col+6, absum[cfg])
            workbook.close()


        import pdb; pdb.set_trace()


Glider()






































#
