
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from nu_animation import glx_anim
from nu_gtplot import netplot
from tqdm import tqdm
import os
import pickle

class Evol:
    def __init__(self,t=100,ng=11,popsize=128,offs=1):
        self.ng = ng
        self.popsize = popsize
        self.offs = offs
        self.genotypes = []
        self.init_population()
        self.trial = Trial(t)

    '''first step: survive different patterns'''
    def evolve(self):
        # generation
        for n_gen in range(self.ng):
            print("\ngeneration {}".format(n_gen))
            gx_data = []
            st0 = (n_gen+1)%4
            if n_gen<4:
                mode="dashes"
                # dash binary pattern
                for dash in range(1,128):
                    dash_glxs = []
                    # genotypes
                    for gi,genotype in enumerate(self.genotypes):
                        glx = self.trial.run(genotype,st0,mode)
                        if glx:
                            dash_glxs.append(glx)
                        print("gen={}, dash={}/127, gl={}/{}, saved={}      ".format(n_gen,dash,gi+1,len(self.genotypes),len(dash_glxs)),end='\r')
            else:
                mode="full"
                dash_glxs=[]
                # genotypes
                for gi,genotype in enumerate(self.genotypes):
                    glx = self.trial.run(genotype,st0,mode)
                    if glx:
                        dash_glxs.append(glx)
                    print("gen={}, dash={}/127, gl={}/{}, saved={}      ".format(n_gen,dash,gi+1,len(self.genotypes),len(dash_glxs)),end='\r')
                # check advances
                dash_glxs = sorted(dash_glxs,key=lambda x:len(x.kdp),reverse=True)
                no = min(len(dash_glxs),5)
                print("\n\ndash results:")
                for gi,glx in enumerate(dash_glxs[:no]):
                    print("{}. kdp={}, cycles={}".format(gi+1,glx.kdp,len(glx.cycles)))
                # refill population
                self.genotypes = []
                for gli in tqdm(range(len(dash_glxs))):
                    for _ in range(self.offs):
                        gt = Genotype(glx=dash_glxs[gli])
                        self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    gt = Genotype()
                    self.genotypes.append(gt)
            self.save_data(n_gen,dash_glxs)
        return gx_data

    def save_data(self,ngen,glxs):
        fname = "g{}_.glxs".format(ngen)
        if not os.path.isdir(os.path.join(os.getcwd(),"glxs")):
            os.mkdir("glxs")
        fpath = os.path.join(os.getcwd(),"glxs",fname)
        with open(fpath,"wb") as glx_file:
            pickle.dump(glxs,glx_file)
        print("\ndata saved at {}\n".format(fpath))

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
