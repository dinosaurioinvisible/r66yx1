
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from nu_animation import glx_anim
from nu_gtplot import netplot
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
                dash_glxs = sorted(dash_glxs,key=lambda x:len(x.cycles),reverse=True)
                for gi,glx in enumerate(dash_glxs):
                    print("{}. kdp={}, cycles={}".format(gi,glx.kdp,len(glx.cycles)))
                # for cycle in dash_glxs[0].cycles:
                #     print(cycle)
                # glx_anim(dash_glxs[0],gx_trial.world)
                netplot(dash_glxs[0])
            # refill population
            self.genotypes = []
            for gl in dash_glxs:
                for _ in range(self.offs):
                    gt = Genotype(glx=gl)
                    self.genotypes.append(gt)
            while len(self.genotypes) < self.popsize:
                gt = Genotype()
                self.genotypes.append(gt)
        return gx_data

    def init_population(self):
        for i in range(self.popsize):
            gt = Genotype()
            self.genotypes.append(gt)





###
