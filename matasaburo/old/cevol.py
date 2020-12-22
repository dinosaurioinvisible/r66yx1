
from collections import defaultdict
from copy import deepcopy
from tqdm import tqdm
import os
import pickle
import numpy as np
from eval_glx import Evaluation

class EvolAlg:
    def __init__(self,time=20,ngens=2001,popsize=500,mrate=0.22,loadpop=False):
        # basic params
        self.time=time
        self.ngens=ngens
        self.popsize=popsize
        self.cgen=0
        self.genotypes = self.define_pop(loadpop)
        # evolutions params
        self.mrate=mrate
        self.nbest=int(popsize*0.25)
        self.nelite=min(1+int(popsize*0.01),3)
        self.ngt_co=int(popsize*0.2)
        # data storage
        self.save_n=min(1+int(popsize*0.1),10)
        # run
        self.evolve()

    '''main evol alg, same as always'''
    def evolve(self):
        for ngen in range(self.ngens):
            print("\ngeneration {}:\n".format(ngen))
            cells_fts=[]
            evx = Evaluation(self.time)
            # evaluate genotypes
            for n_gt in tqdm(range(self.popsize)):
                gt_cells_fts = evx.gt_eval(self.genotypes[n_gt])
                cells_fts.append(gt_cells_fts)
            cells_fts = np.array(cells_fts)
            # sort results for each cell (row 0 is always empty)
            parents_fts=[]
            parents_gts=[]
            for ci,cell_fts in enumerate(cells_fts.T):
                ci_ix_fts = sorted(enumerate(cell_fts),key=lambda x:x[1],reverse=True)[:self.nbest]
                # cell parents fitnesses
                ci_fts = [ci_ix[1] for ci_ix in ci_ix_fts]
                parents_fts.append(ci_fts)
                # cell parents genotypes
                ci_gts = [self.genotypes[ci_ix[0]][ci+1] for ci_ix in ci_ix_fts]
                parents_gts.append(ci_gts)
            parents_fts=np.array(parents_fts)
            # save and print results
            self.save_data(parents_fts,parents_gts)
            print("\ngeneration {} results:\n".format(ngen))
            for pi,ci_px in enumerate(parents_fts):
                print("ci {}: avft={}, best fts: {}".format(pi+1,round(sum(ci_px),2),np.around(ci_px,2)))
            # modify genotypes for next generation
            self.next_gen(parents_fts,parents_gts)
            self.cgen+=1

    '''simple evol fx: elitism + (roulette based) crossover and mutation'''
    def next_gen(self,parents_fts,parents_gts):
        # reset genotypes
        print("\nnew genotypes:\n")
        self.genotypes=[]
        for gi in range(self.popsize):
            gx={}
            self.genotypes.append(gx)
        # parents_gts & parents_fts: correlative sets (1:25)
        for ci in tqdm(range(1,26)):
            # roulette for cell
            fts = parents_fts[ci-1]
            ftprobs = np.array([fts[i]+sum(fts[:i]) for i in range(len(fts))])
            ftsum = np.sum(fts)
            # for each gt
            gxi = 0
            while gxi < self.popsize:
                # elitism
                if gxi<self.nelite:
                    try:
                        self.genotypes[gxi][ci] = deepcopy(parents_gts[ci-1][gxi])
                    except:
                        import pdb; pdb.set_trace()
                    gxi+=1
                # gt crossover
                elif gxi<self.ngt_co:
                    r1,r2 = np.random.uniform(0,ftsum,2)
                    i1 = np.where(r1<=ftprobs)[0][0]
                    i2 = np.where(r2<=ftprobs)[0][0]
                    ci_gx1, ci_gx2 = self.gt_crossover(parents_gts[ci-1][i1],parents_gts[ci-1][i2])
                    self.genotypes[gxi][ci] = ci_gx1
                    self.genotypes[gxi+1][ci] = ci_gx2
                    gxi+=2
                # gt mutations
                else:
                    ri = np.random.uniform(ftsum)
                    gi = np.where(ri<ftprobs)[0][0]
                    ci_gx = self.gt_mutation(parents_gts[ci-1][gi])
                    self.genotypes[gxi][ci] = ci_gx
                    gxi+=1

    '''mix each of the u-arrays for output independently'''
    def gt_crossover(self,gt1,gt2):
        # to avoid numpy inheritance problems
        gt1cell = deepcopy(gt1)
        gt2cell = deepcopy(gt2)
        # each cell has a 512x3 matrix gt
        cg1 = np.zeros((512,3))
        cg2 = np.zeros((512,3))
        # crossing points (for each column)
        k = np.sort(np.random.randint(512,size=(1,3))[0])
        # crossover
        for i,ki in enumerate(k):
            cg1[:,i] = np.concatenate((gt1cell[:ki,i],gt2cell[ki:,i]))
            cg2[:,i] = np.concatenate((gt2cell[:ki,i],gt1cell[ki:,i]))
        # add cell gt to glider gt
        ci_gx1 = deepcopy(cg1)
        ci_gx2 = deepcopy(cg2)
        return ci_gx1,ci_gx2

    '''cell by cell mutation'''
    def gt_mutation(self,gt):
        # deepcopy to avoid inheritance issues
        gtcell = deepcopy(gt)
        # mutation matrix
        mm = np.random.uniform(0,1,size=(512,3))
        # for the 2 binary arrays
        bij = np.where(mm[:,:2]<=self.mrate)
        gtcell[bij] = np.where(gtcell[bij]==1,0,1)
        # for the orientation array (vals={0,1,2,3})
        ox = np.random.randint(0,4,size=(512))
        oij = np.where(mm[:,2]<=self.mrate)
        gtcell[:,2][oij] = ox[oij]
        # add cell gt to glider gt
        ci_gx = deepcopy(gtcell)
        return ci_gx

    '''initial population'''
    def define_pop(self,loadpop):
        genotypes=[]
        # to load old runs
        if loadpop:
            import objload
            self.cgen,genotypes=objload.load()
        # genotypes
        while len(genotypes) < self.popsize:
            gt = self.new_gt()
            genotypes.append(gt)
        return genotypes

    '''create the most simple possible cognitive-like mapping fx
    from 512 (possible inputs) x 3 (for each output) size matrix
    it's initialized at random, the evol cell task is to modulate it
    mappings => uxy:movement - ust:signaling - uo:orientation'''
    def new_gt(self):
        gt={}
        # for each glider's cell
        for ci in range(1,26):
            # move: {0,1}
            uxy=np.random.randint(0,2,size=(512,1))
            # signal: {0,1}
            ust=np.random.randint(0,2,size=(512,1))
            # re-orient: {0,1,2,3} : {N,E,S,W}
            uo=np.random.randint(0,4,size=(512,1))
            u = np.concatenate((uxy,ust,uo),axis=1)
            gt[ci] = u
        return gt


    '''pickle output fx'''
    def save_data(self,parents_fts,parents_gts,dirname="gliders",ext="glx"):
        # init or saving
        if self.cgen==0:
            # the dir path
            self.dirpath=os.path.join(os.getcwd(),dirname)
            if not os.path.isdir(self.dirpath):
                os.mkdir(self.dirpath)
            # define objname
            run=0
            savename=False
            while savename==False:
                self.objname = "{}run{:02}".format(ext,run)
                pfiles = [1 for i in os.listdir(self.dirpath) if self.objname in i]
                if sum(pfiles)>0:
                    run+=1
                else:
                    savename=True
        else:
            # data : parents_fts, parents_gts
            best_avft = np.sum(parents_fts[:,0])
            filedata=[]
            for si in range(self.save_n):
                composed_gx={}
                for ci,ci_gt in enumerate(parents_gts):
                    composed_gx[ci+1]=ci_gt[ci]
                filedata.append([composed_gx,parents_fts[:,si]])
            # save
            filename = "{}_popsize={}_gen{:04}_best_avft{}.{}".format(self.objname,self.popsize,self.cgen,round(best_avft,2),ext)
            filepath = os.path.join(self.dirpath,filename)
            if os.path.isfile(filepath):
                raise("\nfile {} already exists in {}".format(filename,self.dirpath))
            with open(filepath,"wb") as glider_file:
                pickle.dump(filedata,glider_file)
            print("\nsaved at: {}\n".format(filepath))
        # delete previous savings
        temps = sorted([i for i in os.listdir(self.dirpath) if self.objname in i])
        if len(temps)>=7:
            for tempfile in temps[:-2]:
                os.remove(os.path.join(self.dirpath,tempfile))
                print("removed: {}".format(tempfile))


EvolAlg()


































































#
