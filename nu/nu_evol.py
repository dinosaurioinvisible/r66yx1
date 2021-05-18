
from nu_trial import Trial
from nu_genotype import Genotype
from copy import deepcopy
from nu_gtplot import netplot

class EAlg:
    def __init__(self,ng=2,tt=100,popsize=512):
        self.n_gens = ng
        self.tt = tt
        self.popsize = popsize
        self.dashsize = int(popsize/127)
        self.genotypes = []
        self.init_population(128)

    def evolve(self,ng=None):
        # generation
        self.n_gens = ng if ng else self.n_gens
        for n_gen in range(self.n_gens):
            print("\ngeneration {}\n".format(n_gen))
            gx_data = []
            gx_trial = Trial(self.tt)
            # dash binary pattern
            for dash in range(1,128):
                print("")
                dash_data = []
                dash_recs = 0
                max_recs = 0
                saved_glxs = 0
                gx_trial.set_world(dash)
                # genotype
                for gi,genotype in enumerate(self.genotypes):
                    glx = gx_trial.run(deepcopy(genotype))
                    # evaluate and compare
                    if glx.recs > dash_recs:
                        dash_data.append(glx)
                        if len(dash_data)>self.dashsize:
                            dash_data = sorted(dash_data,key=lambda x:x.recs,reverse=True)
                            del(dash_data[-1])
                            dash_recs = dash_data[-1].recs
                            saved_glxs += 1
                            max_recs = dash_data[0].recs
                    print("dash={}/127, gl={}/{}, recurrences={} saved={}      ".format(dash,gi+1,len(self.genotypes),max_recs,saved_glxs),end='\r')
                gx_data.extend(dash_data)
            # refill population
            self.genotypes = []
            for gl in gx_data:
                glgt = Genotype(glx=gl)
                self.genotypes.append(glgt)
            while len(self.genotypes) < self.popsize:
                gt = Genotype(new_gt=True)
                self.genotypes.append(gt)
        return gx_data

    def init_population(self,pop0=None):
        pop0 = self.popsize if not pop0 else pop0
        for i in range(pop0):
            gt = Genotype(new_gt=True)
            self.genotypes.append(gt)





###
