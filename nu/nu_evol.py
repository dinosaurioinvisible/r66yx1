
from nu_trial import Trial
from nu_genotype import Genotype

class EAlg:
    def __init__(self,ng=100,tt=100,popsize=100):
        self.n_gens = ng
        self.tt = tt
        self.popsize = popsize
        self.genotypes = []
        self.n_parents = int(popsize/4)
        self.max_ft = 0
        self.init_population()
        self.evolve()

    def evolve(self):
        for gi in range(self.n_gens):
            print("\generation: {}\n".format(gi))
            fts = []
            gi_trial = Trial(world_objs,self.tt)
            for gt,genotype in enumerate(self.genotypes):
                gt_ft = gi_trial(genotype)
                print("genotype {}/{}, ft={}".format(gi,self.popsize,gi_ft),end='\r')
                fts.append([gt,gt_ft])
                if gt_ft > self.max_ft:
                    self.save_best(gi,gt_ft,genotype)
            fts = sorted(fts, key=lambda x:x[1], reverse=True)[:self.n_parents]
            parents,pfts = zip(*[[deepcopy(self.genotypes[fi[0]]),fi[1]] for fi in fts])
            for i,[pi,pft] in enumerate(zip(parents,pfts)):
                print("{} - {}: ft = {}".format(i+1,pi[0],round(pi[1],2)))
            self.genotypes = []
            self.gen_step(parents,pfts)

    def gen_step(self,parents,fts):
        gts = []
