
from nu_trial import Trial
from nu_genotype import Genotype

class EAlg:
    def __init__(self,ng=64,tt=100,popsize=512):
        self.n_gens = ng
        self.tt = tt
        self.popsize = popsize
        self.genotypes = []
        self.init_population(128)

    def evolve(self):
        for n_gen in range(self.n_gens):
            print("\ngeneration: {}".format(n_gen))
            glxs = []
            gdata = []
            trial = Trial(self.tt)
            for genotype in self.genotypes:
                # data = dash,recs,glx
                gt_data = trial.run(genotype)
                gdata.append(gt_data)
            # evaluate and refill population
            print("")
            self.genotypes = []
            for dash in range(1,128):
                sorted_dash = sorted([gi[dash] for gi in gdata],key=lambda x:x[1],reverse=True)
                if len(sorted_dash)>=4:
                    sorted_dash = sorted_dash[:4]
                print("\ndash pattern={}".format(dash))
                print("best recs:")
                for e,gl in enumerate(sorted_dash):
                    print("    {}: recs={}".format(e+1,gl[1]))
                    glgt = Genotype(glx=recs[2])
                    self.genotypes.append(glgt)
            while len(self.genotypes) < self.popsize:
                gt = Genotype(new_gt=True)
                self.genotypes.append(gt)
        return self.genotypes

    def init_population(self,pop0=None):
        pop0 = self.popsize if not pop0 else pop0
        for i in range(pop0):
            gt = Genotype(new_gt=True)
            self.genotypes.append(gt)
