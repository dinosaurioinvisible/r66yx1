
import os
import sys
import numpy as np
from tqdm import tqdm
from copy import deepcopy
from simulations import evaluate
import loader
import pickle


class EvolRingB:
    def __init__(self,n_gts=100,n_gens=100,n_parents=20,mut_rate=0.15,n_trials=10,timesteps=1000,world_size=25,world_th0=0.2):
        self.n_gts = n_gts
        self.n_gens = n_gens
        self.n_parents = n_parents
        self.mut_rate = mut_rate
        self.n_trials = n_trials
        self.timesteps = timesteps
        self.world_size = world_size
        self.world_th0 = world_th0
        self.genotypes = []
        self.cb_genotypes = []
        self.fpath,self.fname,self.fext = None,None,None
        self.define_fname(name='ringb',dir='ring_exps',ext='rxb')
        self.evolve_menu()

    def evolve(self):
        # generations
        for n_gen in range(self.n_gens):
            # genotypes
            generation_fts = []
            print("")
            for gi,gt in tqdm(enumerate(self.genotypes)):
                ft = evaluate(gt,n_trials=self.n_trials,timesteps=self.timesteps,world_size=self.world_size,world_th0=self.world_th0)
                if ft > 0:
                    generation_fts.append([gi,ft])
            # pick parents
            parents_indexes = sorted(generation_fts,key=lambda x:x[1],reverse=True)[:self.n_parents]
            parents,fts = zip(*[[self.genotypes[gti],fti] for gti,fti in parents_indexes])
            # print data
            print("\ngeneration {}/{}, best genotypes:\n".format(n_gen+1,self.n_gens))
            for fi,ft in enumerate(fts):
                print("{} - ft = {}".format(fi+1,round(ft,2)))
            # create new_genotypes
            self.cb_genotypes = deepcopy(list(parents))
            self.breeding(list(parents),list(fts))
            # output data
            if n_gen%10==0 or (n_gen+1)==self.n_gens:
                self.save_data(gen=n_gen,ft=fts[0])

    def breeding(self,pxs,fts):
        # save best: 3/100
        self.genotypes = deepcopy(pxs[:3])
        # make roulette
        roulette = np.asarray([ft+sum(fts[:fi]) for fi,ft in enumerate(fts)])
        # 33 mutations: 36/100
        for _ in range(33):
            rx = np.random.uniform(0,roulette[-1])
            ri = np.where(roulette>=rx,1,0).nonzero()[0][0]
            px = deepcopy(pxs[ri])
            gt = self.mutate(px)
            self.genotypes.append(gt)
        # 33 recombinations (crossovers): 69/100
        for _ in range(33):
            rx1,rx2 = np.random.uniform(0,roulette[-1],size=(2))
            ri1 = np.where(roulette>=rx1,1,0).nonzero()[0][0]
            ri2 = np.where(roulette>=rx2,1,0).nonzero()[0][0]
            px1 = deepcopy(pxs[ri1])
            px2 = deepcopy(pxs[ri2])
            gt = self.recombine(px1,px2)
            self.genotypes.append(gt)
        # 31 mixed elements mutated: 100/100
        while len(self.genotypes) < self.n_gts:
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
            mi = np.where(mx<self.mut_rate,1,0).nonzero()[0]
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
                gx = gx2 if np.random.uniform()<self.mut_rate else gx1
                gtx[ei][si:sx] = gx[ei][si:sx]
                si += sx
        return gtx

    def evolve_menu(self):
        evol_menu = True
        evol_menu_problem = ''
        while evol_menu==True:
            print('\n\'load\' to load genotypes')
            print('\'ngt\' to change gts number, currently={}'.format(self.n_gts))
            print('\'ngx\' to change generations number, currently={}'.format(self.n_gens))
            print('\'npx\' to change parents number, currently={}'.format(self.n_parents))
            print('\'mr\' to change mutation rate, currently={}'.format(self.mut_rate))
            print('\'nt\' to change number of trials, currently={}'.format(self.n_trials))
            print('\'tt\' to change trial timesteps, currently={}'.format(self.timesteps))
            print('\'ws\' to change world size, currently={}'.format(self.world_size))
            print('\'th\' to change world filling th, currently={}'.format(self.world_th0))
            print('\'x\' to continue')
            print('\'q\' to quit')
            print('{}'.format(evol_menu_problem))
            evol_menu_problem = ''
            em_in = input('\n> ')
            if em_in == 'q':
                print("")
                return
            elif em_in=='x':
                evol_menu = False
            else:
                try:
                    if em_in == 'load':
                        self.cb_genotypes,filename = loader.load(wdir=self.fpath,ext=self.fext,auto=False,return_gts=True)
                        self.fname = '{}_({}_{})'.format(self.fname,filename.split('_')[1],filename.split('_')[-2])
                        print('\nloaded: {}\n'.format(filename))
                    elif em_in == 'ngt':
                        self.n_gts = int(input('gt number? > '))
                    elif em_in == 'ngx':
                        self.n_gens = int(input('generations? > '))
                    elif em_in == 'npx':
                        self.n_parents = int(input('parents? > '))
                    elif em_in == 'mr':
                        self.mut_rate = float(input('mut. rate [0-1]? > '))
                    elif em_in =='nt':
                        self.n_trials = int(input('trials? > '))
                    elif em_in == 'tt':
                        self.timesteps = int(input('timesteps? > '))
                    elif em_in == 'ws':
                        self.world_size = int(input('world size? > '))
                    elif em_in == 'th':
                        self.world_th0 = float(input('world filling threshold [0-1]? > '))
                except:
                    cmin_problem = 'invalid {} input'.format(em_in)
        # fill the remaining gts and run
        self.fill_gts()
        self.evolve()

    def fill_gts(self):
        # keep best ones (or loaded ones)
        if len(self.cb_genotypes)>0:
            self.genotypes.extend(self.cb_genotypes)
        # fill upto defined number of gts
        while len(self.genotypes) < self.n_gts:
            gt = np.random.randint(0,2,size=(4,512))
            self.genotypes.append(gt)

    def define_fname(self,name,dir,ext):
        # output dir path
        self.fext=ext
        self.fpath=os.path.join(os.getcwd(),dir)
        if not os.path.isdir(self.fpath):
            os.mkdir(self.fpath)
        # define file name
        run=0
        savename=False
        while savename==False:
            self.fname = '{}_run{:02}'.format(name,run)
            pfiles = [1 for i in os.listdir(self.fpath) if self.fname in i]
            if sum(pfiles)>0:
                run+=1
            else:
                savename=True

    def save_data(self,gen,ft):
        # save as fname + best current fitness + file extension to cwd
        filename = '{}_g{:04}_ft={}.{}'.format(self.fname,gen+1,round(ft,2),self.fext)
        filepath = os.path.join(self.fpath,filename)
        with open(filepath,'wb') as datapath:
            pickle.dump(self.cb_genotypes,datapath)
        print('\nsaved at: {}\n'.format(filepath))


auto_run = sys.argv[1] if len(sys.argv)>1 else None
if sys.argv[0]=='evol.py':
    if auto_run=='run':
        EvolRingB()

















#
