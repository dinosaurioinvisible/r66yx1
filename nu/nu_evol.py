
import numpy as np
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from pytimedinput import timedInput
from collections import defaultdict
from tqdm import tqdm
import os
import pickle

#TODO: 1 not-useful inner layer

class Evol:
    def __init__(self,mode="dashes",t=100,wsize=100,gens=100,popsize=250,offs=3,fkey="glx"):
        self.gens = gens
        self.popsize = popsize
        self.offs = offs
        self.mode = mode
        self.fkey = fkey
        self.fdir = self.make_fdir()
        self.glxs = []
        self.trial = Trial(t,wsize)
        if self.mode=="dashes":
            self.genotypes = []
            self.init_population()
            self.evolve_dashes()
        elif self.mode=="behavior":
            self.genotypes = set()
            from nu_genotype import set_responses
            self.gt_cycles = set_responses()
            self.evolve_behavior()

    '''evolve behavior'''
    def evolve_behavior(self):
        # generations
        for n_gen in range(self.gens):
            print("\n\ngeneration: {}, genotypes tried: {}\n\n".format(n_gen,len(self.genotypes)))
            # try popsize (2500) gts
            self.glxs = []
            for gi in tqdm(range(self.popsize)):
                # genotype trials
                new_gt = False
                while new_gt == False:
                    gt = np.random.randint(0,8,size=(512))
                    # reserved basic cycles transitions
                    for k,v in self.gt_cycles.items():
                        vx = int("".join(str(i) for i in v),2)
                        gt[k] = vx
                    if tuple(gt) not in self.genotypes:
                        self.genotypes.add(tuple(gt))
                        new_gt = True
                # results = [dx_surv,t1,...,t127,cys] (0:die,1:avoid,2:come back,3:horizontal,4:other)
                gl,gt_results = self.trial.behavior(gt,st0=41)
                self.glxs.append([gl,gt_results])
            self.glxs = sorted(self.glxs,key=lambda x:x[1][0],reverse=True)[:int(self.popsize/10)]
            self.check_data()
            self.glxs = [glxr for glxr in self.glxs if glxr[1][0]>=100]
            if len(self.glxs)>0:
                self.save_data()

    '''first step: survive different patterns'''
    def evolve_dashes(self):
        # generations
        for n_gen in range(self.gens):
            print("\n\ngeneration {}".format(n_gen))
            # env dashes
            for dash in range(1,128):
                # gts
                print("\n")
                self.glxs = []
                dead_by = [0,0,0,0]
                survived = defaultdict(int)
                # to avoid overpopulation
                self.mode = "dashes"
                if len(self.genotypes) > self.popsize:
                    self.mode = "full"
                    backup = deepcopy(self.genotypes[:int(self.popsize/10)])
                # trials
                for gi,gt in enumerate(self.genotypes):
                    # start with north dashes so dash values are (0:127)
                    gl = self.trial.dashes(gt,st0=41,dash=dash)
                    if type(gl)==int:
                        dead_by[gl] += 1
                    elif len(gl.txs)==0:
                        dead_by[3] += 1
                    else:
                        self.glxs.append(gl)
                        survived[(gl.cx_mode,gl.mx_mode)] += 1
                    print("gen={}, mode={}, dash={}/127, gl={}/{}, off={},cols={},tlim={},disc={} saved={} type={} {}".format(n_gen,self.mode,dash,gi+1,len(self.genotypes),dead_by[0],dead_by[1],dead_by[2],dead_by[3],len(self.glxs),survived,""*11),end='\r')
                # results, data check and optional visualization
                self.glxs = sorted(self.glxs,key=lambda x:len(x.txs),reverse=True)
                self.check_data(n_gen,dash)
                # in case full mode was too much
                if self.mode=="full" and len(self.glxs) < self.popsize/10:
                    print("\n\nbackup used, current genotypes={}".format(len(self.glxs)))
                    self.genotypes = backup
                else:
                    self.genotypes = []
                # reset and refill pop
                for gi,gl in enumerate(self.glxs):
                    for _ in range(self.offs):
                        gt = Genotype(glx=gl)
                        self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    gt = Genotype()
                    self.genotypes.append(gt)
                # save (every 16 dashes)
                if dash%16==0:
                    self.glxs = self.glxs[:int(self.popsize/100)]
                    self.save_data(n_gen,dash)
            # generation end
            self.glxs = self.glxs[:int(self.popsize/100)]
            self.save_data(n_gen)

    def check_data(self,n_gen=None,dash=None):
        # menu
        ask,check = True,False
        load,message = True,None
        pdb_check,anim,save,out,ni,nx = True,False,False,False,0,25
        while load==True:
            if self.mode=="dashes":
                # dash results (sorted by number of transients)
                print("\n\ngen={}, dash={}, glxs={} results:".format(n_gen,dash,len(glxs)))
                for gi,gl in enumerate(self.glxs[ni:nx]):
                    print("{} - txs: {}, exgt: {}, dxs: {}".format(gi,len(gl.txs),len(gl.exgt),len(gl.dxs)))
            elif self.mode=="behavior":
                # generation results
                print("\n\ngts tried={}".format(len(self.genotypes)))
                for gi,[gl,gt_res] in enumerate(self.glxs[ni:nx]):
                    dxs = [di+1 for di,dx in enumerate(gt_res[1:]) if dx>0]
                    beh = [np.sum(np.where(gt_res[1:-1]==1,1,0)),np.sum(np.where(gt_res[1:-1]==2,1,0)),np.sum(np.where(gt_res[1:-1]==3,1,0)),np.sum(np.where(gt_res[1:-1]==4,1,0))]
                    print("{} - cys: {} - memb_rxs: {} - core_rxs: {} - beh: {} - dxs: {}: \n{}".format(gi,len(gl.cys),len(gl.memb_rxs),len(gl.core_rxs),beh,gt_res[0],dxs))
            # if timed out, just print best 25
            if ask:
                # optinal data check
                rx,non_rx = timedInput("\n\nto check glxs data press any key before 10s",7)
                if not non_rx:
                    check = True
                else:
                    for tx in range(3,-1,-1):
                        rx,non_rx = timedInput("..{}..".format(tx),1)
                        if not non_rx:
                            check = True
                            break
                ask = False
            if not check:
                return
            # if error message
            if message:
                print("\n{}\n".format(message))
                message = None
            # menu options
            print("\n[p]db={}, [a]nim={}, [s]ave={}, [o]utput={}, [r]ange={}:{}".format(pdb_check,anim,save,out,ni,nx))
            n_gl = input("\ngl index or \'q\' to quit: _ ")
            if n_gl=="q" or n_gl=="quit":
                return
            elif n_gl=="r":
                nr = input("\nstart,end? _ ")
                try:
                    ni,nx = int(nr[0]),int(nr[1])
                    glxs[ni,nx]
                except:
                    message = "invalid glxs range"
            elif n_gl=="p":
                pdb_check = True if pdb_check==False else False
            elif n_gl=="a":
                anim = True if anim==False else False
            elif n_gl=="s":
                save = True if save==False else False
            elif n_gl=="o":
                out = True if out==False else False
            else:
                try:
                    if self.mode=="dashes":
                        glx = self.glxs[int(n_gl)]
                    elif self.mode=="behavior":
                        glx,results = self.glxs[int(n_gl)]
                    if pdb_check:
                        print("\nresults = {}\n".format(results))
                        import pdb; pdb.set_trace()
                    if anim==True or save==True:
                        import nu_animation
                        if self.mode=="dashes":
                            nu_animation.glx_anim(glx,self.trial.world,show=anim,save=save)
                        elif self.mode=="behavior":
                            nu_animation.glx_anim(glx,self.trial.world,basic=True,show=anim,save=save)
                            gt_anim = Genotype()
                            for fi,fx in enumerate(glx.exgt):
                                fx = tuple([int(i) for i in np.binary_repr(fx,3)])
                                gt_anim.exgt[fi] = fx
                            self.trial.dashes(gt_anim,dash=127,anim=True)
                            self.trial.full(gt_anim,anim=True)
                    if out:
                        if self.mode=="dashes":
                            self.save_single(glx,n_gen,dash,int(n_gl)+1)
                        elif self.mode=="behavior":
                            self.save_single(glx)
                except:
                    message = "invalid input"

    '''create folder for saving data'''
    def make_fdir(self):
        # start from glxs_001
        fdir = "{}s_mode={}_run={:0=3d}".format(self.fkey,self.mode,1)
        if os.path.isdir(fdir):
            last_folder = sorted([i for i in os.listdir() if self.mode in i],key=lambda x:x[-3:])[-1]
            fn = int(last_folder.split("=")[-1])+1
            fdir = "{}s_mode={}_run={:0=3d}".format(self.fkey,self.mode,fn)
        os.mkdir(fdir)
        return os.path.join(os.getcwd(),fdir)

    def save_single(self,glx,n_gen=None,dash=None,n_glx=None):
        if self.mode=="dashes":
            fname = "g{}dx{}x{}_txs={}_exgt={}_dxs={}.{}".format(n_gen,dash,n_glx,len(glx.txs),len(glx.exgt),len(glx.dxs),self.fkey)
        elif self.mode=="behavior":
            fname = "gtx={}.{}".format(len(self.genotypes),self.fkey)
        fpath = os.path.join(self.fdir,fname)
        with open(fpath,"wb") as glx_path:
            pickle.dump(glx,glx_path)
        print("glx agent saved at \n{}".format(fpath))

    def save_data(self,n_gen=None,dash=None):
        if self.mode=="dashes":
            if dash:
                fname = "g{:0=3d}_dx{:0=3d}.{}s".format(n_gen,dash,self.fkey)
            else:
                fname = "g{:0=3d}.{}s".format(n_gen,self.fkey)
            iname = "g{:0=3d}_info.txt".format(n_gen)
        elif self.mode=="behavior":
            fname = "gts={}.{}s".format(len(self.genotypes),self.fkey)
            iname = "genotypes_info.txt"
        fpath = os.path.join(self.fdir,fname)
        ipath = os.path.join(self.fdir,iname)
        if self.mode=="dashes":
            with open(ipath,"w") as info:
                info.write("\n\ngeneration: {}".format(n_gen))
                info.write("\tdx: {}\n\n".format(dash if dash else ""))
                for gi,gl in enumerate(self.glxs):
                    info.write("{} - txs={}, exgt={}, dxs={}\n".format(gi+1,len(gl.txs),len(gl.exgt),len(gl.dxs)))
                info.close()
        elif self.mode=="behavior":
            # create info file
            if not os.path.isfile(ipath):
                with open(ipath,"w") as info:
                    info.write("?")
                info.close()
            # clear and write again
            with open(ipath,"r+") as info:
                info.truncate(0)
                info.write("\n\nnumber of genotypes tried: {}\n\n".format(len(self.genotypes)))
                for gt in self.genotypes:
                    info.write("\n{}".format(gt))
                info.close()
        # pickle save
        with open(fpath,"wb") as glxs_path:
            if self.mode=="dashes":
                pickle.dump(self.glxs,glxs_path)
            elif self.mode=="behavior":
                pickle.dump(self.glxs,glxs_path)
        print("\ndata saved at {}\n".format(fpath))

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
