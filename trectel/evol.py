
import numpy as np
from simulation import evaluate
from tqdm import tqdm
from copy import deepcopy
import pickle

class Evol:
    def __init__(self,genotypes=[],n_gts=100,n_gens=100,n_parents=20,mut_rate=0.15,n_trials=10,n_steps=100,world_th0=0.2):
        self.n_gts = n_gts
        self.n_gens = n_gens
        self.n_parents = n_parents
        self.mr = mut_rate
        self.n_trials = n_trials
        self.n_steps = n_steps
        self.world_th0 = world_th0
        self.genotypes = genotypes
        self.backup = None
        self.create_genotypes()
        self.evolve()

    # def save(self):
        # output gts with pickle
        # TODO

    def evolve_cont(self,genotypes=[],n_gts=None,n_gens=None,n_parents=None,mut_rate=None,n_trials=None,n_steps=None,world_th0=None):
        # gts
        self.genotypes.extend(genotypes)
        self.create_genotypes()
        # opt redefine variables
        self.n_gts = n_gts
        self.n_gens = n_gens
        self.n_parents = n_parents
        self.mr = mut_rate
        self.n_trials = n_trials
        self.n_steps = n_steps
        self.world_th0 = world_th0
        self.evolve()

    def evolve(self):
        # generations
        for n_gen in range(self.n_gens):
            # genotypes
            generation_fts = []
            print("")
            for gi,gt in tqdm(enumerate(self.genotypes)):
                ft = evaluate(gt,n_trials=self.n_trials,n_steps=self.n_steps,world_th0=self.world_th0)
                if ft > 0:
                    generation_fts.append([gi,ft])
            # pick parents
            parents_indexes = sorted(generation_fts,key=lambda x:x[1],reverse=True)[:self.n_parents]
            parents,fts = zip(*[[self.genotypes[gti],fti] for gti,fti in parents_indexes])
            # print data
            print("\ngeneration {}, best genotypes:\n".format(n_gen+1))
            for fi,ft in enumerate(fts):
                print("{} - ft = {}".format(fi+1,round(ft,2)))
            # create new_genotypes
            self.backup = parents
            self.breeding(parents,fts)
        # output data
        # TODO

    def breeding(self,pxs,fts):
        # save best: 1/100
        self.genotypes = [deepcopy(pxs[0])]
        # make roulette
        roulette = np.asarray([ft+sum(fts[:fi]) for fi,ft in enumerate(fts)])
        # 33 mutations: 34/100
        for _ in range(33):
            rx = np.random.uniform(0,roulette[-1])
            ri = np.where(roulette>=rx,1,0).nonzero()[0][0]
            px = deepcopy(pxs[ri])
            gt = self.mutate(px)
            self.genotypes.append(gt)
        # 33 recombinations (crossovers): 67/100
        for _ in range(33):
            rx1,rx2 = np.random.uniform(0,roulette[-1],size=(2))
            ri1 = np.where(roulette>=rx1,1,0).nonzero()[0][0]
            ri2 = np.where(roulette>=rx2,1,0).nonzero()[0][0]
            px1 = deepcopy(pxs[ri1])
            px2 = deepcopy(pxs[ri2])
            gt = self.recombine(px1,px2)
            self.genotypes.append(gt)
        # 33 mixed elements mutated: 100/100
        for _ in range(33):
            gt = np.zeros((4,512))
            for ei in range(4):
                rx = np.random.uniform(0,roulette[-1])
                ri = np.where(roulette>=rx,1,0).nonzero()[0][0]
                ex = deepcopy(pxs[ri][ei])
                if np.random.uniform() > 0.5:
                    ex = self.mutate(ex)[0]
                gt[ei] = ex
            self.genotypes.append(gt)

    def mutate(self,gx):
        # check if is a full gt or a gt chain
        if len(gx.shape) < 2:
            gx = np.array([gx])
        # mutate
        for ei,ex in enumerate(gx):
            mx = np.random.uniform(size=len(ex))
            mi = np.where(mx<self.mr,1,0).nonzero()[0]
            for mxi in mi:
                ex[mxi] = 0 if ex[mxi] == 1 else 1
        return gx

    def recombine(self,gx1,gx2):
        # new gt
        gtx = np.zeros((4,512)).astype(int)
        # for every element
        for ei in range(4):
            # gt subdivisions (1:4, so 2 to 5 parts)
            si = 0
            subs = np.random.randint(1,5)
            sxs = sorted(list(set(np.random.randint(2,510,size=subs))))+[512]
            for sx in sxs:
                # choose parent element gt part and copy to new gt
                gx = gx1 if np.random.uniform()<0.5 else gx2
                gtx[ei][si:sx] = gx[ei][si:sx]
                si += sx
        return gtx

    def create_genotypes(self):
        while len(self.genotypes) < self.n_gts:
            gt = np.random.randint(0,2,size=(4,512))
            self.genotypes.append(gt)
