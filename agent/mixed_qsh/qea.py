
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from copy import deepcopy
from tqdm import tqdm
import qeval
import qanim

#TODO: after 100g create a new file for saving
#TODO: fusion and fision

class EvolAlg():
    def __init__(self, time=300, popsize=180, load_pop=True):
        # internal (as defined by M. Quinn (2001) and Shibuya et al.)
        self.popsize=popsize
        self.time=time
        self.n_gens=2000
        self.cgen=0
        self.n_parents=33
        # quinn (2001):
        # self.dmax=25
        # self.crossover_rate=0.6
        # self.micromuts=3.5
        self.addgx_prob=0.01
        self.delgx_prob=0.02
        self.addcx_prob=0.025
        self.delcx_prob=0.05
        self.ids=0
        # shibuya et al:
        self.cmax=10
        self.dmax=40
        self.elite=2
        self.crossover_rate=0.2
        self.crossover_prob=0.5
        self.mut_rate=0.05
        # for saving the history of all genotypes
        self.genotypes = []
        # init population (from clonal types)
        self.population = []
        self.init_population(load_pop)
        # saving
        self.max_ft = 15
        self.filename=""
        self.define_filename()
        self.save_step=1
        self.save_data()
        # run ea
        self.evolve()


    def evolve(self):
        # for each generation
        for i_gen in range(self.cgen,self.n_gens):
            print("\ngeneration: {}\n".format(i_gen))
            # for each genotype
            parents = []
            for gt in range(len(self.population)):
                genotype = self.population[gt]
                eval = qeval.Evaluation(genotype,self.time)
                # save object everytime there is a new max
                print("gt{}: ft={}".format(gt, round(eval.av_ft,2)))
                if eval.av_ft > self.max_ft:
                    name = "{}_gen={}_ft={}_gt{}={}".format(self.index,i_gen,round(eval.av_ft,2),gt,[gx[0] for gx in genotype])
                    print("new max: {}".format(name))
                    qanim.sim_animation(eval, show=False, save=True, fname=name)
                    # self.save_eval(eval)
                    self.max_ft = eval.av_ft
                # add genotype's results to list
                parents.append([deepcopy(eval.genotype), eval.av_ft])
            # sort by fitness, print results and save
            parents = sorted(parents, key=lambda x:x[1], reverse=True)[:self.n_parents]
            print("\ngeneration {} sorted agents:\n".format(i_gen))
            for enum,px in enumerate(parents):
                print("{} - ft = {}, genotype: {}".format(enum, round(px[1],2), [gene[0] for gene in px[0]]))
            # save this generation's genotypes to pickle
            gen_gts = deepcopy(parents)
            self.genotypes.append(gen_gts)
            if len(self.genotypes)%self.save_step==0:
                self.save_data()
            # next generation
            self.next_gen(parents)


    # from Shibuya et al. (Quinn, 2001 dont explain this)
    def next_gen(self, parents):
        # normalization of ft values (max=120, min=-40)
        for px in parents:
            norm_ft = 0 if px[1] <= 0 else px[1]
            px.append(norm_ft)
        # elitism (replicate best 2)
        self.population = []
        print("\nelitism:")
        for enum,px in enumerate(parents[:self.elite]):
            print("gt{}: ft={}, norm_ft={}, gt={}".format(enum,round(px[1],2),round(px[2],2),[gx[0] for gx in px[0]]))
            self.population.append(deepcopy(px[0]))
        # 20% from crossover by roulette strategy
        print("\nroulette:")
        # for normalized probabilities
        ftsum = sum(px[1] for px in parents)
        print("ftsum={}".format(ftsum))
        for px in parents:
            prob = px[2]/ftsum
            px.append(prob)
        psum = sum(px[3] for px in parents)
        # roulette selection
        for gi in range(int(self.popsize*self.crossover_rate/2)):
            r1 = np.random.uniform(0,psum)
            p1 = 0
            for px in parents:
                p1 += px[3]
                if r1 <= p1:
                    pgt1 = px
                    break
            r2 = np.random.uniform(0,psum)
            p2 = 0
            for px in parents:
                p2 += px[3]
                if r2 <= p2:
                    pgt2 = px
                    break
            # px = [0:gt, 1:ft, 2:norm_ft, 3:prob([0:1])]
            print("gt1_ft={}, gt1_prob={}, gt1={}".format(round(pgt1[1],2), round(pgt1[3],2), [gx[0] for gx in pgt1[0]]))
            print("gt2_ft={}, gt2_prob={}, gt2={}".format(round(pgt2[1],2), round(pgt2[3],2), [gx[0] for gx in pgt2[0]]))
            ngt1,ngt2 = self.crossover(deepcopy(pgt1[0]),deepcopy(pgt2[0]))
            print("gt{}: gtx1 => ngt1={}".format(len(self.population),[gx[0] for gx in ngt1]))
            print("gt{}: gtx2 => ngt2={}".format(len(self.population)+1,[gx[0] for gx in ngt2]))
            self.population.extend([ngt1,ngt2])
        # the reamining are mutations (it isn't explicit from where)
        print("\nmutations:")
        while len(self.population) < self.popsize:
            r = np.randon.uniform(0,psum)
            p = 0
            for px in parents:
                if r<=p:
                    ngt = self.mutate(deepcopy(parents[cgt][0]))
                    print("gt{}: => genotype: {}".format(len(self.population),[gx[0] for gx in ngt]))
                    self.population.append(ngt)
                    break

    # mutator operator (from Quinn's thesis)
    def mutate(self, gt
        , xr=200, yr=250, sr=50, mr=30, ur=5):
        # info
        zaddgx = None
        zdelgx = None
        zaddcx_in = 0
        zaddcx_out = 0
        zdelcx_in = 0
        zdelcx_out = 0
        # macro-mutations: addition and deletion of genes
        if np.random.uniform(0,1) <= self.addgx_prob:
            gene = self.create_gene()
            zaddgx = gene[0]
            gt.append(gene)
        # del gen
        if np.random.uniform(0,1) <= self.delgx_prob:
            if len(gt) > 1:
                dg = np.random.randint(0,len(gt))
                zdelgx = gt[dg][0]
                del(gt[dg])
        # inside gene mutations
        for gene in gt:
            # macro-mutations addition/deletion of connections
            if np.random.uniform(0,1) <= self.addcx_prob:
                io = np.random.choice([True,False])
                zx = np.random.uniform(0,xr)
                zw = np.random.uniform(-ur,ur)
                if io:
                    # new input connection
                    zy = np.random.uniform(0,yr-mr)
                    gene[6].append([zx,zy,zw])
                    zaddcx_in += 1
                else:
                    # new output connection
                    zy = np.random.uniform(sr,yr)
                    gene[7].append([zx,zy,zw])
                    zaddcx_out += 1
            # deletion
            if np.random.uniform(0,1) <= self.delcx_prob:
                io = np.random.choice([True,False])
                if io:
                    if len(gene[6]) > 0:
                        dg = np.random.randint(len(gene[6]))
                        del(gene[6][dg])
                        zdelcx_in += 1
                else:
                    if len(gene[7]) > 0:
                        dg = np.random.randint(len(gene[7]))
                        del(gene[7][dg])
                        zdelcx_out += 1
            # micro-mutations (as in Shibuya et al, mixed with Quinn's)
            # neuron cartesian coordinates (bounded to the neural space)
            dx = np.random.normal(0,xr*0.5)
            x = gene[1]+dx
            if x < 0:
                x = np.random.uniform(0,gene[1])
            elif x > xr:
                x = np.random.uniform(gene[1],xr)
            gene[1] = x
            dy = np.random.normal(0,(yr-sr-mr)*0.5)
            y = gene[2]+dy
            if y < sr:
                y = np.random.uniform(sr,gene[2])
            elif y > yr-mr:
                y = np.random.uniform(gene[2],(yr-mr))
            gene[2] = y
            # thresholds (unbounded, initialized between [-5,5])
            dT = np.random.normal(0,ur)
            gene[3] += dT
            # decay parameters (bounded between [0:1])
            dga = np.random.normal(0,0.5)
            ga = gene[4] + dga
            if ga < 0:
                ga = np.random.uniform(0,gene[4])
            elif ga > 1:
                ga = np.random.uniform(gene[4],1)
            gene[4] = ga
            dgb = np.random.normal(0,0.5)
            gb = gene[5] + dgb
            if gb < 0:
                gb = np.random.uniform(0,gene[5])
            elif gb > 1:
                gb = np.random.uniform(gene[5],1)
            gene[5] = gb
            # weights (unbounded, initialized between [-5:5])
            for wi in range(len(gene[6])):
                dw = np.random.normal(0,ur)
                gene[6][wi][2] += dw
            for wo in range(len(gene[7])):
                dw = np.random.normal(0,ur)
                gene[7][wo][2] += dw
        print("+gen:{}, -gen:{}, +cx_in={},+cx_out={}, -cx_in={},-cx_out={}".format(zaddgx,zdelgx,zaddcx_in,zaddcx_out,zdelcx_in,zdelcx_out))
        return gt


    # recombination operator (from Quinn's thesis)
    def crossover(self, gt1, gt2):
        # crossover
        new_gt1 = []
        new_gt2 = []
        # pair genes with the same id
        par_gt1 = sorted([gx1 for gx1 in gt1 if gx1[0] in [gx2[0] for gx2 in gt2]], key=lambda x:x[0])
        par_gt2 = sorted([gx2 for gx2 in gt2 if gx2[0] in [gx1[0] for gx1 in gt1]], key=lambda x:x[0])
        # unpaired genes
        unp_gt1 = [gx1 for gx1 in gt1 if gx1 not in par_gt1]
        unp_gt2 = [gx2 for gx2 in gt2 if gx2 not in par_gt2]
        np.random.shuffle(unp_gt1)
        np.random.shuffle(unp_gt2)
        # crossover (50% chances) (paired must be of the same length)
        for pgx in zip(par_gt1,par_gt2):
            i1 = np.random.choice([0,1])
            i2 = 1 if i1 == 0 else 0
            new_gt1.append(pgx[i1])
            new_gt2.append(pgx[i2])
        # unpaired genes crossover (same length)
        for ugx in zip(unp_gt1,unp_gt2):
            i1 = np.random.choice([0,1])
            i2 = 1 if i1 == 0 else 0
            new_gt1.append(ugx[i1])
            new_gt2.append(ugx[i2])
        # remaining unpaired genes (if different length)
        rem_gt = unp_gt1[len(unp_gt2):] if len(unp_gt1) > len(unp_gt2) else unp_gt2[len(unp_gt1):]
        for rgx in rem_gt:
            new_gt1.append(rgx) if np.random.choice([True,False]) else new_gt2.append(rgx)
        # send back
        return new_gt1, new_gt2


    # initialization (clonal)
    def init_population(self, load_pop):
        # create (or complete) population
        if load_pop == True:
            wdir = os.path.join(os.getcwd(), "qobjs")
            objs = sorted([i for i in os.listdir(wdir) if "obj" in i])
            select_obj = True
            select_gen = False
            # select object
            while select_obj == True:
                print("\n")
                for enum, obj_filename in enumerate(objs):
                    print("{} - {}".format(enum, obj_filename))
                n_in = input("\nselect object: ")
                try:
                    n_obj = int(n_in)
                    n_obj_filename = objs[n_obj]
                    obj_path = os.path.join(wdir, n_obj_filename)
                    with open(obj_path, "rb") as ea_exp:
                        generations = pickle.load(ea_exp)
                    select_gen = True
                    obj_popsize = len(generations[0])
                except:
                    print("couldn't open object")
                # select generation
                while select_gen==True:
                    print("\n")
                    for enum,gen in enumerate(generations):
                        fts = [gt[1] for gt in generations[enum]]
                        avft = sum(fts)/len(fts)
                        print("gen {}, av_ft={}, fts: {} ...".format(enum, round(avft,2), np.around(fts[:5],2)))
                    print("\n")
                    print("\"p\" to plot fitness evolution")
                    print("\"s\" to change popsize, currently={} (loaded object popsize={})".format(self.popsize,obj_popsize))
                    print("\"b\" to go back")
                    g_in = input("\ngeneration?: ")
                    if g_in=="b":
                        select_gt=False
                    elif g_in=="s":
                        change_popsize = True
                        while change_popsize == True:
                            pop_in = input("popsize?: ")
                            try:
                                self.popsize = int(pop_in)
                                change_popsize = False
                            except:
                                print("invalid input")
                    elif g_in =="p" or g_in=="plot":
                        plt.plot(np.arange(0,len(generations)),np.asarray([sum([gt[1] for gt in gen])/len(gen) for gen in generations]))
                        plt.plot(np.arange(0,len(generations)),np.asarray([gen[0][1] for gen in generations]))
                        plt.xlabel("Generation")
                        plt.ylabel("Fitness")
                        plt.show()
                    else:
                        try:
                            n_gen = int(g_in)
                            self.genotypes = generations
                            self.population = [gt[0] for gt in generations[n_gen]]
                            self.cgen = n_gen+1
                            select_gen = False
                            select_obj = False
                        except:
                            print("\ninvalid input")
            print("population loaded from {}:\ngeneration {}, popsize={}".format(obj_path,self.cgen,self.popsize))
        # adjust to popsize (in case)
        if len(self.population) > self.popsize:
            self.population = self.population[:self.popsize]
        # create genotypes
        print("=> {} agents to adjust to popsize={}".format(self.popsize-len(self.population),self.popsize))
        while len(self.population) < self.popsize:
            gt = self.create_genotype()
            self.population.append(gt)

    # Shibuya et al version
    # def create_genotype(self, n_genes=20, n_in=8, n_out=4, rg=5):
    #     genotype = []
    #     for gi in range(n_genes):
    #         T = np.random.uniform(-rg,rg)
    #         wx_in = [np.random.uniform(-rg,rg) for wi in range(n_in)]
    #         wx_out = [np.random.uniform(-rg,rg) for wo in range(n_out)]
    #         ga = np.random.uniform(0,1)
    #         gb = np.random.uniform(0,1)
    #         gene = [T]+wx_in+wx_out+[ga,gb]
    #         genotype.append(gene)

    # QUINN version
    def create_genotype(self, min_genes=6, max_genes=8
        , max_in=8, min_out=1, max_out=8):
        # predefined values from Quinn's thesis
        genotype = []
        for _ in range(np.random.randint(min_genes,max_genes+1)):
            gene = self.create_gene(max_in=max_in,min_out=min_out,max_out=max_out)
            genotype.append(gene)
        return genotype

    def create_gene(self, max_in=2, min_out=0, max_out=2
        , xr=200, yr=250, sr=50, mr=30, ur=5):
        x = np.random.uniform(0,xr)
        y = np.random.uniform(sr, yr-mr)
        th = np.random.uniform(-ur,ur)
        ga = np.random.uniform(0,1)
        gb = np.random.uniform(0,1)
        l_in = []
        l_out = []
        for _ in range(np.random.randint(0,max_in+1)):
            ix = np.random.uniform(0,xr)
            iy = np.random.uniform(0,yr-mr)
            iw = np.random.uniform(-ur,ur)
            l_in.append([ix,iy,iw])
        for _ in range(np.random.randint(min_out,max_out+1)):
            ox = np.random.uniform(0,xr)
            oy = np.random.uniform(sr,yr)
            ow = np.random.uniform(-ur,ur)
            l_out.append([ox,oy,ow])
        gene = [self.ids,x,y,th,ga,gb,l_in,l_out]
        self.ids += 1
        return gene


    # define filename for saving
    def define_filename(self):
        # dirpath
        dirname = "qobjs"
        self.dir_path = os.path.join(os.getcwd(),dirname)
        if not os.path.isdir(self.dir_path):
            os.mkdir(self.dir_path)
        try:
            index = "{:03}".format(int(sorted([i for i in os.listdir(self.dir_path) if ".qobj" in i])[-1].split("_")[1])+1)
        except:
            index = "000"
        self.index = "qrun_{}".format(index)

    # save
    def save_data(self):
        i_name = "{}_pop={}_gen={}.qobj".format(self.index, self.popsize, len(self.genotypes))
        i_path = os.path.join(self.dir_path, i_name)
        # look for previous temps
        temps = sorted([i for i in os.listdir(self.dir_path) if self.index in i])
        # safety check
        if os.path.isfile(i_path):
            import time
            print("\nfile already exists")
            i_path += time.ctime()
        # save with pickle
        with open(i_path, "wb") as exp_file:
            pickle.dump(self.genotypes, exp_file)
        print("\nobject saved at: \n{}\n".format(i_path))
        # delete previous temps
        if len(temps)>=1:
            for tempfile in temps[:-1]:
                os.remove(os.path.join(self.dir_path,tempfile))
                print("removed temporal file: {}".format(tempfile))
        print("")


EvolAlg()








































    ##
