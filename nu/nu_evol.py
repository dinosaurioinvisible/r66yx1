
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from pytimedinput import timedInput
import os
import pickle

class Evol:
    def __init__(self,t=100,wsize=100,gens=100,popsize=1000,offs=3):
        self.gens = gens
        self.popsize = popsize
        self.offs = offs
        self.genotypes = []
        self.save_path = None
        self.init_population()
        self.trial = Trial(t,wsize)
        self.evolve_dashes()

    '''first step: survive different patterns'''
    def evolve_dashes(self):
        # generations
        for n_gen in range(10):
            glxs = []
            print("\n\ngeneration {}".format(n_gen))
            # env dashes
            for dash in range(1,128):
                # gts
                off,col,lim = 0,0,0
                for gi,gt in enumerate(self.genotypes):
                    # start with north dashes so dash values are (0:127)
                    tgl = self.trial.run(gt,st0=41,mode="dashes",dash=dash)
                    if tgl[0]:
                        glxs.append(tgl[0])
                    else:
                        off += tgl[1]
                        col += tgl[2]
                        lim += tgl[3]
                    print("gen={}, dash={}/127, gl={}/{}, off={},cols={},tlim={}, saved={}{}".format(n_gen,dash,gi+1,len(self.genotypes),off,col,lim,len(glxs),""*10),end='\r')
                # reset pop
                self.genotypes = []
                # dash results (sorted by number of transients)
                print("\n\ngen={}, dash={} results:".format(n_gen,dash))
                glxs = sorted(glxs,key=lambda x:len(x.txs),reverse=True)
                for gi,gl in enumerate(glxs):
                    if len(gl.txs)>0:
                        print("{} - cycles={}, transients={}, responses={}, dashes={}".format(gi+1,len(gl.cycles),len(gl.txs),len(gl.exgt),len(gl.dxs)))
                        # refill pop
                        for _ in range(self.offs):
                            gt = Genotype(glx=gl)
                            self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    gt = Genotype()
                    self.genotypes.append(gt)
            # generation step: optional animation and save
            self.save_data(n_gen,glxs)
            rx,timedOut = timedInput("Press any key before 5 seconds for pdb",5)
            if not timedOut:
                import pdb; pdb.set_trace()

    '''second step: random starting conditions and encounters'''
    def evolve_complex(self):
        pass

    def save_data(self,ngen,glxs):
        glxs_dir = "glxs_0"
        fname = "g{}_.glxs".format(ngen)
        if not self.save_path:
            if os.path.isdir(glxs_dir):
                last_file = sorted([i for i in os.listdir() if "glxs_" in i])[-1]
                glxs_dir = "glxs_{}".format(int(last_file[5:])+1)
            os.mkdir(glxs_dir)
            self.save_path = os.path.join(os.getcwd(),glxs_dir)
        fpath = os.path.join(self.save_path,fname)
        glxs_info = os.path.join(self.save_path,"info.txt")
        with open(glxs_info,"w") as info:
            info.write("\n\n\ngeneration {}, gliders: {}\n".format(ngen,len(glxs)))
            for gi,glx in enumerate(glxs):
                info.write("{}:\ncycles:\n{}\nknown dashes:\n{}".format(gi+1,glx.cycles,glxs.kdp))
        with open(fpath,"wb") as glx_file:
            pickle.dump(glxs,glx_file)
        print("\ndata saved at {}\n".format(fpath))

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
