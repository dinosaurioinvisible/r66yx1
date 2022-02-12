
import os
import numpy as np
from simulation import evaluate
from tqdm import tqdm
from copy import deepcopy
import loader
import pickle

class Evol:
    def __init__(self,load=False,n_gts=100,n_gens=100,n_parents=20,mut_rate=0.15,n_trials=10,n_steps=200,world_size=25,world_th0=0.22):
        self.n_gts = n_gts
        self.n_gens = n_gens
        self.n_parents = n_parents
        self.mr = mut_rate
        self.n_trials = n_trials
        self.n_steps = n_steps
        self.world_size = world_size
        self.world_th0 = world_th0
        self.genotypes = []
        self.cb_genotypes = []
        # for saving
        self.fname = ''
        self.lname = ''
        self.ext = 'rx'
        self.path = ''
        self.define_fname(fname='ring',wdir='ring_exps')
        if load:
            self.load_gts()
        else:
            self.create_genotypes()
            self.evolve()

    def load_gts(self):
        loadname,self.genotypes = loader.load(default=False,return_gts=True)
        self.lname = '_'+''.join(loadname.split('.')[0].split('_')[1:])
        self.evolve_cont()

    def evolve(self):
        # generations
        for n_gen in range(self.n_gens):
            # genotypes
            generation_fts = []
            print("")
            for gi,gt in tqdm(enumerate(self.genotypes)):
                ft = evaluate(gt,n_trials=self.n_trials,n_steps=self.n_steps,world_size=self.world_size,world_th0=self.world_th0)
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
            self.cb_genotypes = deepcopy(parents)
            self.breeding(parents,fts)
            # output data
            if n_gen%5==0 or (n_gen+1)==self.n_gens:
                self.save_data(data=parents,gen=n_gen,ft=fts[0])


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

    def evolve_cont(self):
        # menu for opt changes
        cont_menu = True
        cmin_problem = None
        while cont_menu==True:
            print('\n\'name\' to change output filename, currently: {}'.format(self.fname))
            print('\'gt\' to change gts number, currently={}'.format(self.n_gts))
            print('\'gx\' to change generations number, currently={}'.format(self.n_gens))
            print('\'px\' to change parents number, currently={}'.format(self.n_parents))
            print('\'mr\' to change mutation rate, currently={}'.format(self.mr))
            print('\'nt\' to change number of trials, currently={}'.format(self.n_trials))
            print('\'tt\' to change trial timesteps, currently={}'.format(self.n_steps))
            print('\'ws\' to change world size, currently={}'.format(self.world_size))
            print('\'th\' to change world filling th, currently={}'.format(self.world_th0))
            print('return to continue')
            print('\'q\' to quit')
            if cmin_problem:
                print('\n{}'.format(cmin_problem))
                cmin_problem = None
            cmin = input('\n> ')
            if cmin == 'q':
                return
            elif cmin=='':
                cont_menu = False
            else:
                try:
                    if cmin == 'name':
                        name = input('name? > ')
                        ['_{}'.format(i) for i in self.fname]
                        self.fname = '{}_{}_{}'.format(name,self.fname.split('_')[1],self.fname.split('_')[2])
                    elif cmin == 'gt':
                        self.n_gts = int(input('gt number? > '))
                    elif cmin == 'gx':
                        self.n_gens = int(input('generations? > '))
                    elif cmin == 'px':
                        self.n_parents = int(input('parents? > '))
                    elif cmin == 'mr':
                        self.mr = float(input('mut. rate [0-1]? > '))
                    elif cmin =='nt':
                        self.n_trials = int(input('trials? > '))
                    elif cmin == 'tt':
                        self.n_steps = int(input('timesteps? > '))
                    elif cmin == 'ws':
                        self.world_size = int(input('world size? > '))
                    elif cmin == 'th':
                        self.world_th0 = float(input('world filling threshold [0-1]? > '))
                except:
                    cmin_problem = 'invalid {} input'.format(cmin)
        self.create_genotypes()
        self.evolve()

    def create_genotypes(self):
        # gts (if loaded or/and current best gts)
        if len(self.cb_genotypes)>0:
            self.genotypes.extend(self.cb_genotypes)
        while len(self.genotypes) < self.n_gts:
            gt = np.random.randint(0,2,size=(4,512))
            self.genotypes.append(gt)

    def define_fname(self,fname,wdir):
        # the dir path
        self.path=os.path.join(os.getcwd(),wdir)
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        # define file name
        run=0
        savename=False
        while savename==False:
            self.fname = "{}_run{:02}".format(fname,run)
            pfiles = [1 for i in os.listdir(self.path) if self.fname in i]
            if sum(pfiles)>0:
                run+=1
            else:
                savename=True

    def save_data(self,data,gen,ft):
        # define output name
        filename = '{}_g{:04}ft{}{}.{}'.format(self.fname,gen,round(ft),self.lname,self.ext)
        filepath = os.path.join(self.path,filename)
        if os.path.isfile(filepath):
            print('file {} already exists, in {}'.format(filename,filepath))
            self.fname = input('define a new filename: ')
            filename = '{}_g{:04}ft{}.{}'.format(self.fname,gen,round(ft),self.ext)
            filepath = os.path.join(self.path,filename)
        # save
        with open(filepath,'wb') as datapath:
            pickle.dump(data,datapath)
        print("\nsaved at: {}\n".format(filepath))










#
