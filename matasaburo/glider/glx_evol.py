
from collections import defaultdict
from copy import deepcopy
from tqdm import tqdm
import os
import time
import pickle
import numpy as np
from glx_eval import Evaluation

class EvolAlg:
    def __init__(self,time=5,n_cells=9,n_gens=2001,popsize=1000,mrate=0.2,loadpop=False):
        # basic params
        self.time=time
        self.n_cells=n_cells
        self.n_gens=n_gens
        self.popsize=popsize
        # file handling
        self.cgen=0
        self.path=""
        self.fname=""
        self.genotypes=[]
        self.define_pop(loadpop,wdir="gliders",name="glx")
        # evolutions params
        self.mrate=mrate
        self.n_best=int(popsize*0.25)
        self.n_elite=min(1+int(popsize*0.01),1)
        self.n_gt_cxo=int((popsize*0.15)/2)
        self.n_cell_cxo=int((popsize*0.15)/2)
        self.n_fusions=int(popsize*0.05)
        self.n_fisions=int((popsize*0.1)/2)
        # data output
        self.save_n=min(1+int(popsize*0.1),10)
        self.evolve()

    '''main evol alg, same as always'''
    def evolve(self):
        for ngen in range(self.n_gens):
            print("\n\ngeneration {}:\n".format(ngen))
            gen_results = []
            evx = Evaluation(self.time)
            # evaluate genotypes
            for n_gt in tqdm(range(self.popsize)):
                glx_wft,glx_fts = evx.gt_eval(self.genotypes[n_gt])
                gen_results.append([glx_wft,n_gt,glx_fts])
            ###
            # select the best 1/4, print and save
            avft = sum([gi[0] for gi in gen_results])/len(gen_results)
            gen_results = sorted(gen_results, key=lambda x:x[0], reverse=True)[:self.n_best]
            print("\ngeneration {} results:\n\npop average ft={}\n".format(ngen,round(avft,2)))
            # results: [av_ft, n_gt, trials fts]
            for gi,gi_results in enumerate(gen_results[:int(self.n_best/4)]):
                c1,c2,c3,c4 = [round(ci,2) for ci in gi_results[2]]
                print("gt{}: wft={}, c1={}, c2={}, c3={}, c4={}".format(gi+1,round(gi_results[0],2),c1,c2,c3,c4))
            self.save_data(gen_results)
            ###
            # modify genotypes for next generation
            parents = [[gi[0],self.genotypes[gi[1]]] for gi in gen_results]
            self.next_gen(parents)
            self.cgen+=1

    '''simple evol fx: elitism + (roulette based) crossover and mutation'''
    def next_gen(self,parents):
        # elitism (1% aprox)
        self.genotypes=[deepcopy(px[1]) for px in parents[:self.n_elite]]
        print("\nelitism: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')
        # fts params for roulette
        fts = np.array([px[0] for px in parents])
        ftprobs = np.array([fts[i]+sum(fts[:i]) for i in range(len(fts))])
        ftsum = np.sum(fts)
        # gt crossover
        print()
        for xe in range(self.n_gt_cxo):
            r1,r2 = np.random.uniform(0,ftsum,2)
            i1 = np.where(r1<=ftprobs)[0][0]
            i2 = np.where(r2<=ftprobs)[0][0]
            self.gt_crossover(parents[i1][1],parents[i2][1])
            print("gt crossovers: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')
        # cell crossover
        print()
        for xe in range(self.n_cell_cxo):
            r1,r2 = np.random.uniform(0,ftsum,2)
            i1 = np.where(r1<=ftprobs)[0][0]
            i2 = np.where(r2<=ftprobs)[0][0]
            self.cell_crossover(parents[i1][1],parents[i2][1])
            print("cell crossovers: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')
        # gt fusion
        print()
        for xe in range(self.n_fusions):
            r1,r2 = np.random.uniform(0,ftsum,2)
            i1 = np.where(r1<=ftprobs)[0][0]
            i2 = np.where(r2<=ftprobs)[0][0]
            self.gt_fusion(parents[i1][1],parents[i2][1])
            print("gt fusion: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')
        # gt fision
        print()
        for xe in range(self.n_fisions):
            r = np.random.uniform(ftsum)
            gi = np.where(r<=ftprobs)[0][0]
            self.gt_fision(parents[gi][1])
            print("gt fision: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')
        # mutate (all the remaining)
        print()
        n_mutations = self.popsize-len(self.genotypes)
        for xe in range(n_mutations):
            r = np.random.uniform(ftsum)
            gi = np.where(r<=ftprobs)[0][0]
            self.gt_mutation(parents[gi][1])
            print("mutations: population={}/{}".format(len(self.genotypes),self.popsize),end='\r')

    '''mutation of the already known responses'''
    def gt_mutation(self,gt):
        gx=self.new_gt()
        for ci in range(1,self.n_cells+1):
            gtcell = deepcopy(gt[ci])
            for ri in gtcell:
                # mutate
                dxy=gtcell[ri][0]
                if np.random.uniform(0,1)<=self.mrate:
                    dxy=0 if dxy==1 else 1
                dst=gtcell[ri][1]
                if np.random.uniform(0,1)<=self.mrate:
                    dst=0 if dst==1 else 1
                do=gtcell[ri][2]
                if np.random.uniform(0,1)<=self.mrate:
                    do = np.random.randint(-1,2)
                # append new responses
                gx[ci][ri] = [dxy,dst,do]
        self.genotypes.append(deepcopy(gx))

    '''fision of a gt into 2 smaller gts (to free/renew responses)'''
    def gt_fision(self,gt):
        gx1=self.new_gt()
        gx2=self.new_gt()
        # random material to gx1 or gx2
        for ci in range(1,self.n_cells+1):
            gtcell = deepcopy(gt[ci])
            for ri in gtcell:
                if np.random.choice([True,False]):
                    gx1[ci][ri] = gtcell[ri]
                else:
                    gx2[ci][ri] = gtcell[ri]
        # append to gts
        self.genotypes.append(deepcopy(gx1))
        self.genotypes.append(deepcopy(gx2))

    '''fusion of 2 gts'''
    def gt_fusion(self,gt1,gt2):
        gx=self.new_gt()
        for ci in range(1,self.n_cells+1):
            # to avoid numpy inheritance problems
            gt1cell = deepcopy(gt1[ci])
            gt2cell = deepcopy(gt2[ci])
            # fusion (gt1 is predominant)
            for ri in gt2cell:
                gx[ci][ri]=gt2cell[ri]
            for ri in gt1cell:
                gx[ci][ri]=gt1cell[ri]
        # append to gts
        self.genotypes.append(deepcopy(gx))

    '''exchange of complete cells gt'''
    def cell_crossover(self,gt1,gt2):
        gx1=self.new_gt()
        gx2=self.new_gt()
        for ci in range(1,self.n_cells+1):
            # to avoid numpy inheritance problems
            gt1cell = deepcopy(gt1[ci])
            gt2cell = deepcopy(gt2[ci])
            # cell by cell
            if np.random.uniform(0,1)<=self.mrate:
                gx1[ci] = gt2cell
                gx2[ci] = gt1cell
            else:
                gx1[ci] = gt1cell
                gx2[ci] = gt2cell
        # append to gts
        self.genotypes.append(deepcopy(gx1))
        self.genotypes.append(deepcopy(gx2))

    '''mix each of the u-arrays for output independently'''
    def gt_crossover(self,gt1,gt2):
        gx1=self.new_gt()
        gx2=self.new_gt()
        # for each cell in glider
        for ci in range(1,self.n_cells+1):
            # to avoid numpy inheritance problems
            gt1cell = deepcopy(gt1[ci])
            gt2cell = deepcopy(gt2[ci])
            # each cell has a limited number of known responses
            rx = np.array([ri1 for ri1 in gt1cell]+[ri2 for ri2 in gt2cell])
            # crossover gt1 -> gt2
            for ri in gt1cell:
                if np.random.uniform(0,1)<=self.mrate:
                    gx2[ci][ri] = gt1cell[ri]
                else:
                    gx1[ci][ri] = gt1cell[ri]
            # crossover gt2 -> gt1
            for ri in gt2cell:
                if np.random.uniform(0,1)<=self.mrate:
                    gx1[ci][ri] = gt2cell[ri]
                else:
                    gx2[ci][ri] = gt2cell[ri]
        # append to gts
        self.genotypes.append(deepcopy(gx1))
        self.genotypes.append(deepcopy(gx2))


    '''empty genotype (dict of dicts)'''
    def new_gt(self):
        gt={}
        for ci in range(1,self.n_cells+1):
            gt[ci]={}
        return gt

    '''initial population'''
    def define_pop(self,loadpop,wdir="gliders",name="glx"):
        # to load old runs
        if loadpop:
            import glx_load
            self.genotypes,fname=glx_load.load(wdir=wdir,ext=name,default=False,anim=False,save_video=False,return_data=False,return_gts=True)
            self.cgen=int([i for i in fname.split("_") if "gen" in i][0].split("=")[1])
            name="{}c".format([i for i in fname.split("_") if "glxrun" in i][0])
        # genotypes
        while len(self.genotypes) < self.popsize:
            gt=self.new_gt()
            self.genotypes.append(gt)
        self.define_fname(wdir,name)

    '''helper fx for creating the filename'''
    def define_fname(self,wdir,name):
        # the dir path
        self.path=os.path.join(os.getcwd(),wdir)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        # define file name
        run=0
        savename=False
        while savename==False:
            self.fname = "{}run{:02}".format(name,run)
            pfiles = [1 for i in os.listdir(self.path) if self.fname in i]
            if sum(pfiles)>0:
                run+=1
            else:
                savename=True

    '''pickle output fx'''
    def save_data(self,gen_results,ext="glx"):
        # data(i) : [w_ft, n_gt, [fi1,fi2,fi3,fi4]]
        best_ft = gen_results[0][0]
        filedata = [[gi[0],self.genotypes[gi[1]],gi[2]] for gi in gen_results[:self.save_n] if gi[0]>0]
        # save
        filename = "{}_ncells={}_popsize={}_gen={:04}_mr={}_bwft={}.{}".format(self.fname,self.n_cells,self.popsize,self.cgen,self.mrate,round(best_ft,2),ext)
        filepath = os.path.join(self.path,filename)
        if os.path.isfile(filepath):
            raise("\nfile {} already exists in {}".format(filename,self.path))
        with open(filepath,"wb") as glider_file:
            pickle.dump(filedata,glider_file)
        print("\nsaved at: {}\n".format(filepath))
        # delete previous savings
        temps = sorted([i for i in os.listdir(self.path) if self.fname in i])
        if len(temps)>=7:
            for tempfile in temps[:-2]:
                os.remove(os.path.join(self.path,tempfile))
                print("removed: {}".format(tempfile))


EvolAlg()









#
