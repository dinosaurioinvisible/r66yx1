
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from pytimedinput import timedInput
import os
import pickle

#TODO: 1 not-useful inner layer

class Evol:
    def __init__(self,t=100,wsize=100,gens=100,popsize=2500,offs=3,fkey="glx"):
        self.gens = gens
        self.popsize = popsize
        self.offs = offs
        self.genotypes = []
        self.mode = "dashes"
        self.fkey = fkey
        self.fdir = self.make_fdir()
        self.init_population()
        self.trial = Trial(t,wsize)
        self.evolve_dashes()

    '''first step: survive different patterns'''
    def evolve_dashes(self):
        # generations
        for n_gen in range(10):
            print("\n\ngeneration {}".format(n_gen))
            # env dashes
            for dash in range(1,128):
                # gts
                print("\n")
                glxs = []
                dead_by = [0,0,0,0]
                # to avoid overpopulation
                self.mode = "dashes"
                if len(self.genotypes) > self.popsize:
                    self.mode = "full"
                    backup = deepcopy(self.genotypes[:int(self.popsize/10)])
                # trials
                for gi,gt in enumerate(self.genotypes):
                    # start with north dashes so dash values are (0:127)
                    gl = self.trial.run(gt,st0=41,mode=self.mode,dash=dash)
                    if type(gl)==int:
                        dead_by[gl] += 1
                    elif len(gl.txs)==0:
                        dead_by[3] += 1
                    else:
                        glxs.append(gl)
                    print("gen={}, mode={}, dash={}/127, gl={}/{}, off={},cols={},tlim={},disc={} saved={} {}".format(n_gen,self.mode,dash,gi+1,len(self.genotypes),dead_by[0],dead_by[1],dead_by[2],dead_by[3],len(glxs),""*11),end='\r')
                # results, data check and optional visualization
                glxs = sorted(glxs,key=lambda x:len(x.txs),reverse=True)
                self.check_data(glxs,n_gen,dash)
                # in case full mode was too much
                if self.mode=="full" and len(glxs) < self.popsize/10:
                    print("\n\nbackup used, current genotypes={}".format(len(glxs)))
                    self.genotypes = backup
                else:
                    self.genotypes = []
                # reset and refill pop
                for gi,gl in enumerate(glxs):
                    for _ in range(self.offs):
                        gt = Genotype(glx=gl)
                        self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    # cx_mode = np.random.choice(["genotype","automata"])
                    # mx_mode = np.random.choice(["delta","basic","all"])
                    # gt = Genotype(glx=None,cx_mode=cx_mode,mx_mode=mx_mode)
                    gt = Genotype()
                    self.genotypes.append(gt)
                # save (every 16 dashes)
                if dash%16==0:
                    self.save_data(glxs[:int(self.popsize/100)],n_gen,dash)
            # generation end
            self.save_data(glxs[:int(self.popsize/100)],n_gen)

    '''second step: random starting conditions and encounters'''
    def evolve_complex(self):
        pass

    def check_data(self,glxs,n_gen,dash):
        # optinal data check
        check = False
        rx,non_rx = timedInput("\n\nto check glxs data press any key before 10s",7)
        if not non_rx:
            check = True
        else:
            for tx in range(3,-1,-1):
                rx,non_rx = timedInput("..{}..".format(tx),1)
                if not non_rx:
                    check = True
                    break
        # menu
        load,message = True,None
        pdb_check,anim,save,out,ni,nx = True,False,False,False,0,25
        while load==True:
            # dash results (sorted by number of transients)
            print("\n\ngen={}, dash={}, glxs={} results:".format(n_gen,dash,len(glxs)))
            for gi,gl in enumerate(glxs[ni:nx]):
                print("{} - txs: {}, exgt: {}, dxs: {}".format(gi,len(gl.txs),len(gl.exgt),len(gl.dxs)))
            # if timed out, just print best 25
            if not check:
                return
            # if error message
            if message:
                print("\n{}\n".format(message))
                message = None
            # menu options
            print("[p]db={}, [a]nim={}, [s]ave={}, [o]utput={}, [r]ange={}:{}".format(pdb_check,anim,save,out,ni,nx))
            n_gl = input("gl index or \'q'\ to quit: _ ")
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
                    glx = glxs[int(n_gl)]
                    if pdb_check:
                        print("\nglx = {}\n".format(glx))
                        import pdb; pdb.set_trace()
                    if anim==True or save==True:
                        import nu_animation
                        nu_animation.glx_anim(glx,self.trial.world,show=anim,save=save)
                    if out:
                        self.save_single(glx,n_gen,dash,int(n_gl)+1)
                except:
                    message = "invalid input"

    '''create folder for saving data'''
    def make_fdir(self):
        # start from glxs_001
        fdir = "{}s_run={:0=3d}".format(self.fkey,1)
        if os.path.isdir(fdir):
            last_folder = sorted([i for i in os.listdir() if self.fkey in i])[-1]
            fn = int(last_folder.split("=")[-1])+1
            fdir = "{}s_{:0=3d}".format(self.fkey,fn)
        os.mkdir(fdir)
        return os.path.join(os.getcwd(),fdir)

    def save_single(self,glx,n_gen,dash,n_glx):
        fname = "g{}dx{}x{}_txs={}_exgt={}_dxs={}.{}".format(n_gen,dash,n_glx,len(glx.txs),len(glx.exgt),len(glx.dxs),self.fkey)
        fpath = os.path.join(self.fdir,fname)
        with open(fpath,"wb") as glx_path:
            pickle.dump(glx,glx_path)
        print("glx agent saved at \n{}".format(fpath))

    def save_data(self,glxs,n_gen,dash=None):
        if dash:
            fname = "g{:0=3d}_dx{:0=3d}.{}s".format(n_gen,dash,self.fkey)
        else:
            fname = "g{:0=3d}.{}s".format(n_gen,self.fkey)
        iname = "g{:0=3d}_inf0.txt".format(n_gen,self.fkey)
        fpath = os.path.join(self.fdir,fname)
        ipath = os.path.join(self.fdir,iname)
        with open(ipath,"w") as info:
            info.write("\n\ngeneration: {}".format(n_gen))
            info.write("\tdx: {}\n\n".format(dash if dash else ""))
            for gi,gl in enumerate(glxs):
                info.write("{} - txs={}, exgt={}, dxs={}\n".format(gi+1,len(gl.txs),len(gl.exgt),len(gl.dxs)))
        with open(fpath,"wb") as glxs_path:
            pickle.dump(glxs,glxs_path)
        print("\ndata saved at {}\n".format(fpath))

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
