
import numpy as np
import ag_genotype
import ag_trial
import animation
from copy import deepcopy
import pickle
import os

class Evol:
    def __init__(self,gens=100,tt=100,popsize=100):
        self.generations = gens
        self.trial_t = tt
        self.popsize = popsize
        self.n_parents = int(popsize/4)
        self.genotypes = []
        self.max_ft = 0
        self.mut_rate = 0.2
        self.best = []
        self.init_population()
        self.evolve()

    def evolve(self):
        for gen_i in range(self.generations):
            print("\ngeneration: {}\n".format(gen_i))
            fts = []
            gen_trial = ag_trial.Trial(t=self.trial_t)
            for gi,genotype in enumerate(self.genotypes):
                gi_ft = gen_trial.run_trial(genotype)
                print("genotype {}/{}, ft={}".format(gi,self.popsize,gi_ft),end='\r')
                fts.append([gi,gi_ft])
                if gi_ft > self.max_ft:
                    self.save_best(gen_i,gi_ft,genotype)
            fts = sorted(fts, key=lambda x:x[1], reverse=True)[:self.n_parents]
            parents = [[deepcopy(self.genotypes[fi[0]]),fi[1]] for fi in fts]
            for i,pi in enumerate(parents):
                print("{} - {}: ft = {}".format(i+1,pi[0],round(pi[1],2)))
            self.genotypes = []
            self.next_gen(parents)

    def next_gen(self,parents):
        # separate genotypes and fts
        gts = [pi[0] for pi in parents]
        fts = np.asarray([pi[1] for pi in parents])
        # for early gens where ft<0
        if fts[-1] < 0:
            fts = fts + abs(fts[-1])
        print("fts:")
        print(fts)
        # elite (1 only)
        self.genotypes = [deepcopy(gts[0])]
        # mutations (~ half)
        roulette = np.asarray([sum(fts[:fi+1]) for fi in range(len(fts))])
        print("roulette:")
        print(roulette)
        while len(self.genotypes) < self.popsize/2:
            ri = np.random.uniform(0,roulette[-1])
            for i,fi in enumerate(roulette):
                if ri <= fi:
                    gx = deepcopy(gts[i])
                    gx.mutate(self.mut_rate)
                    self.genotypes.append(gx)
                    break
        # breeding (remaining half)
        while len(self.genotypes) < self.popsize:
            r1,r2 = np.random.uniform(0,roulette[-1],size=2)
            for i1,fi in enumerate(roulette):
                if r1 <= fi:
                    gx1 = deepcopy(gts[i1])
                    break
            for i2,fi in enumerate(roulette):
                if r2 <= fi:
                    gx2 = gts[i2]
                    break
            gx1.combine(gx2,self.mut_rate)
            self.genotypes.append(gx1)

    def save_best(self,gen_i,gi_ft,genotype):
        print("\nnew max: {} -> {}\n".format(round(self.max_ft,2),round(gi_ft,2)))
        self.max_ft = gi_ft
        self.best.append(deepcopy(genotype))
        if len(self.best) > 10:
            del(self.best[0])
        iname = "gen={}_ft={}_id={}.gtx".format(gen_i,round(gi_ft,2),str(genotype))
        ipath = os.path.join(os.getcwd(),iname)
        with open(ipath,"wb") as gtx_file:
            pickle.dump(genotype,gtx_file)
        print("\ngenotype object saved at {}\n".format(ipath))


    def init_population(self):
        while len(self.genotypes) < self.popsize:
            self.genotypes.append(ag_genotype.Genotype())
