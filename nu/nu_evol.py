
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from nu_animation import glx_anim
from nu_gtplot import netplot
import os
import pickle

class Evol:
    def __init__(self,ng=3,tt=100,popsize=128,offs=2):
        self.ng = ng
        self.tt = tt
        self.popsize = popsize
        self.offs = offs
        self.genotypes = []
        self.init_population()

    '''first step: survive different patterns'''
    def evolve_dashes(self):
        # generation
        for n_gen in range(self.ng):
            print("\ngeneration {}".format(n_gen))
            gx_data = []
            gx_trial = Trial(tt=self.tt)
            # dash binary pattern
            for dash in range(1,128):
                dash_glxs = []
                gx_trial.set_world(mode="dashes",dash=dash)
                # genotypes
                for gi,genotype in enumerate(self.genotypes):
                    glx = gx_trial.dash_trial(genotype)
                    if glx:
                        dash_glxs.append(glx)
                    print("dash={}/127, gl={}/{}, saved={}      ".format(dash,gi+1,len(self.genotypes),len(dash_glxs)),end='\r')
                # check advances
                print("\n\ndash results:")
                dash_glxs = sorted(dash_glxs,key=lambda x:len(x.kdp),reverse=True)
                for gi,glx in enumerate(dash_glxs):
                    print("{}. kdp={}, cycles={}".format(gi,glx.kdp,len(glx.cycles)))
                # refill population
                self.genotypes = []
                for gl in dash_glxs:
                    for _ in range(self.offs):
                        gt = Genotype(glx=gl)
                        self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    gt = Genotype()
                    self.genotypes.append(gt)
            self.save_data(n_gen,dash_glxs)
        return gx_data

    def save_data(self,ngen,glxs):
        fname = "g{}_.glxs".format(ngen)
        fpath = os.path.join(os.getcwd(),fname)
        with open(fpath,"wb") as glx_file:
            pickle.dump(glxs)
        print("\ndata saved at {}\n".format(fpath))

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
