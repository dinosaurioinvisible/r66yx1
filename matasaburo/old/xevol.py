
from collections import defaultdict
from copy import deepcopy
from tqdm import tqdm
import os
import pickle
import numpy as np
from xeval import Evaluation

class EvolAlg:
    def __init__(self,time=20,ngens=2000,popsize=500,mrate=0.22,loadpop=False):
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
        self.nrandom=min(1+int(popsize*0.02),5)
        self.ngt_co=int(popsize*0.15)
        self.ncell_co=int(popsize*0.15)
        # data storage
        self.save_n=min(1+int(popsize*0.1),10)
        # run
        self.evolve()

    '''main evol alg, same as always'''
    def evolve(self):
        for ngen in range(self.ngens):
            print("\ngeneration {}:\n".format(ngen))
            gen_results = []
            evx = Evaluation(self.time)
            # evaluate genotypes
            for n_gt in tqdm(range(self.popsize)):
                trial_data = evx.gt_eval(self.genotypes[n_gt])
                gt_ft = trial_data[0]
                gen_results.append([gt_ft,n_gt,trial_data])
            ####
            # select the best 1/4, print and save
            avft = sum([g[0] for g in gen_results])/len(gen_results)
            gen_results = sorted(gen_results, key=lambda x:x[0], reverse=True)[:self.nbest]
            print("\ngeneration {} results:\n\npop average ft={}\n".format(ngen,round(avft,2)))
            # results: [av_ft, n_gt, trial data]
            for gi,gi_results in enumerate(gen_results[:self.save_n*2]):
                av_ft=round(gi_results[0],2)
                # trials data: [av_ft,c1,c2,c3,c4]]
                c1,c2,c3,c4 = [round(ci[0],2) for ci in gi_results[2][1:]]
                print("gt{}: wft={}, c1={}, c2={}, c3={}, c4={}".format(gi+1,av_ft,c1,c2,c3,c4))
            self.save_data(gen_results)
            ####
            # modify genotypes for next generation
            parents = [[gi[0],self.genotypes[gi[1]]] for gi in gen_results]
            self.next_gen(parents)
            self.cgen+=1

    '''simple evol fx: elitism + (roulette based) crossover and mutation'''
    def next_gen(self,parents):
        # elitism (1% aprox)
        self.genotypes=[deepcopy(px[1]) for px in parents[:self.nelite]]
        # fts params for roulette
        fts = np.array([px[0] for px in parents])
        ftprobs = np.array([fts[i]+sum(fts[:i]) for i in range(len(fts))])
        ftsum = np.sum(fts)
        # for early generation (if ftsum is very very low)
        # if ftsum<10:
        #     fts = np.array([0.1+fi*10 for fi in fts])
        #     ftprobs = np.array([fts[i]+sum(fts[:i]) for i in range(len(fts))])
        #     ftsum = np.sum(fts)
        # gt2 crossover
        for oxo in range(int(self.ngt_co/2)):
            r1,r2 = np.random.uniform(0,ftsum,2)
            i1 = np.where(r1<=ftprobs)[0][0]
            i2 = np.where(r2<=ftprobs)[0][0]
            self.gt_crossover(parents[i1][1],parents[i2][1])
        # cell crossover
        for oxo in range(int(self.ncell_co/2)):
            r1,r2 = np.random.uniform(0,ftsum,2)
            i1 = np.where(r1<=ftprobs)[0][0]
            i2 = np.where(r2<=ftprobs)[0][0]
            self.cell_crossover(parents[i1][1],parents[i2][1])
        # new totally random ones
        for new in range(self.nrandom):
            gx = self.new_gt()
            self.genotypes.append(gx)
        # mutate (all the others)
        while len(self.genotypes) < self.popsize:
            r = np.random.uniform(ftsum)
            gi = np.where(r<=ftprobs)[0][0]
            self.mutation_fx(parents[gi][1])

    '''change of complete cells genotypes'''
    def cell_crossover(self,gt1,gt2):
        gx1={}
        gx2={}
        # according to mut rate
        rx = np.random.uniform(0,1,size=(22))
        rx = np.where(rx<self.mrate,1,0)
        # cell by cell
        for i in range(22):
            ci=i+1
            if rx[i]==1:
                gx1[ci] = gt1[ci]
                gx2[ci] = gt2[ci]
            else:
                gx1[ci] = gt2[ci]
                gx2[ci] = gt1[ci]
        # add to genotypes
        self.genotypes.append(deepcopy(gx1))
        self.genotypes.append(deepcopy(gx2))

    '''mix each of the u-arrays for output independently'''
    def gt_crossover(self,gt1,gt2):
        # new gts
        gx1={}
        gx2={}
        # for each cell in glider
        for ci in range(1,23):
            # to avoid numpy inheritance problems
            gt1cell = deepcopy(gt1[ci])
            gt2cell = deepcopy(gt2[ci])
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
            gx1[ci] = cg1
            gx2[ci] = cg2
        # append to gts
        self.genotypes.append(deepcopy(gx1))
        self.genotypes.append(deepcopy(gx2))

    '''cell by cell mutation'''
    def mutation_fx(self,gt):
        # for each cell in gt
        gx = {}
        for ci in range(1,23):
            # deepcopy to avoid inheritance issues
            gtcell = deepcopy(gt[ci])
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
            gx[ci] = gtcell
        # add to gts
        self.genotypes.append(deepcopy(gx))

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
        for ci in range(1,23):
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
    def save_data(self,gen_results,dirname="gliders",ext="glx"):
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
            # data : [genotype, trials data: [av_ft,c1,c2,c3,c4]]
            # ci = [c_ft, c_prog, c_glider_states]
            best_ft = gen_results[0][0]
            filedata = [[self.genotypes[gi[1]],gi[2]] for gi in gen_results[:self.save_n] if gi[0]>0]
            # save
            filename = "{}_popsize={}_gen{:04}_bestft{}.{}".format(self.objname,self.popsize,self.cgen,round(best_ft,2),ext)
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
