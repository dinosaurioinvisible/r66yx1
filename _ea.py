
import numpy as np
import _genotype
import _trial
import _trial_animation
import random
import pickle
import os


class Evolve():
    def __init__(self, n_gen=33, n_groups=10, n_trials=10\
        , genotype=None\
        , n_agents=1\
        , n_trees=10\
        , trial_t=1000\
        , mut_rate=0.1\
        , anim=False
        , save=True):
        # groups of agents
        self.n_gen = n_gen
        self.n_groups = n_groups
        self.n_trials = n_trials
        self.n_agents = n_agents
        self.n_trees = n_trees
        self.trial_t = trial_t
        self.mut_rate = mut_rate
        # opts
        self.anim = anim
        self.debug = False
        # opt load genotype
        if not genotype:
            self.genotypes = [_genotype.Genotype() for i in range(self.n_groups)]
        else:
            self.genotypes = [genotype for i in range(self.n_groups)]
        # for saving cases
        self.total_e = 0
        self.av_e = 0
        self.max_e = 0
        self.good_cases = []
        # run
        self.simulation()

    def simulation(self):
        # for each generation
        for n in range(self.n_gen):
            print("\n")
            groups_data = []
            # raise difficulty (less trees)
            # tx_lv = int(n/10)
            # n_trees = self.n_trees - tx_lv
            # randomly select number of trees
            n_trees = int(random.uniform(1,self.n_trees+1))
            # for each group:
            for ng in range(self.n_groups):
                print("\n")
                group_fts = []
                # for each trial (same genotype, but different world)
                for nt in range(self.n_trials):
                    print("generation: {}/{}, group: {}/{}, trial: {}/{}, agents: {}, trees:{}".format(n+1,self.n_gen, ng+1,self.n_groups, nt+1,self.n_trials, self.n_agents, n_trees))
                    # run trial
                    xtrial = _trial.Trial(t=self.trial_t, genotype=self.genotypes[ng], n_agents=self.n_agents, world=None, n_trees=n_trees)
                    # fitness = sum of energies * how many agents are alive
                    ags_e = np.array([ag.e for ag in xtrial.agents])
                    living_ags = sum(np.where(ags_e>0, 1, ags_e))
                    xft = sum(ags_e) * living_ags/self.n_agents
                    group_fts.append(xft)
                    for i in range(len(ags_e)):
                        print("agent{} energy: {}".format(i+1, round(ags_e[i],2)))
                    print("group fitness: {}".format(round(group_fts[-1],2)))

                # weight trial performances for group
                sorted_fts = sorted(group_fts, reverse=True)
                ft_sum = 0
                for i in range(self.n_trials):
                    ft_sum += (i+1)*group_fts[i]
                w_ft = 2/(self.n_trials*(self.n_trials+1)) * ft_sum
                groups_data.append([w_ft, xtrial.genotype])

            # get best group
            best = sorted(groups_data, key=lambda x:x[0], reverse=True)[0]
            print("\nbest group weighted fitness: {}".format(round(best[0],2)))
            # print average energy
            self.total_e += best[0]
            self.av_e = self.total_e/(n+1)
            print("average energy until now: {}".format(round(self.av_e,2)))
            # save if good (over average)
            if best[0] > self.av_e:
                self.good_cases.append([n+1, best[0], best[1]])
                print("group over average, added to good cases")
                # for debugging
                if self.debug and n+1>=10:
                    os.system("osascript -e \"set Volume 10\" ")
                    os.system("open -a vlc ~/desktop/hadouken.mp4")
                    _trial_animation.sim_animation(xtrial.world, xtrial.agents, self.trial_t)
                    import pdb; pdb.set_trace()
            # print good cases
            if len(self.good_cases) > 0:
                print("good cases = {})".format([(i[0],round(i[1],2)) for i in self.good_cases]))
            # animation
            if self.anim:
                _trial_animation.sim_animation(xtrial.world, xtrial.agents, self.trial_t)

            # next generation (assuming clonal approach)
            # best genotype replication
            self.genotypes = [best[1]]
            # best genotype mutations
            for n in range(4):
                self.mutate(best[1])
            # rest: breeding through roulette type selection
            sorted_best = sorted(groups_data, key=lambda x:x[0], reverse=True)[:int(self.n_groups/3)]
            parents = [i for i in sorted_best if i[0] > 0]
            if len(parents) < 2:
                while len(self.genotypes) < self.n_groups:
                    self.mutate(best[1])
            else:
                self.breed(parents)

        # "alarm" after ending
        os.system("osascript -e \"set Volume 5\" ")
        os.system("open -a vlc ~/desktop/hadouken.mp4")
        # os.system("open -a vlc ~/desktop/brigth-engelberts-free-me-now.mp3")

    def mutate(self, xgenotype):
        # connectivity weights
        wx = xgenotype.W
        # for every weight, if within mut rate, mutate from [-0.1, 0.1]
        for i in range(len(wx)):
            for j in range(len(wx[i])):
                if random.uniform(0,1)<self.mut_rate:
                    wx[i][j] += random.uniform(-0.1,0.1)
        # check no w[i][j] goes out of [-1,1]
        wx = np.where(wx<-1, -1, wx)
        wx = np.where(wx>1, 1, wx)
        # veto weights
        vx = xgenotype.V
        for i in range(len(vx)):
            for j in range(len(vx[i])):
                if random.uniform(0,1)<self.mut_rate/10:
                    wx[i][j] += random.uniform(-0.05,0.05)
                # also possible to come back to zero
                if random.uniform(0,1)<self.mut_rate/10:
                    wx[i][j] = 0
        vx = np.where(vx<-1, -1, vx)
        vx = np.where(vx>1, 1, vx)
        # thresholds
        if random.uniform(0,1)<self.mut_rate:
            ut = xgenotype.ut + random.uniform(-0.05,0.05)
        else:
            ut = xgenotype.ut
        if random.uniform(0,1)<self.mut_rate:
            lt = xgenotype.lt + random.uniform(-0.05,0.05)
        else:
            lt = xgenotype.lt
        if random.uniform(0,1)<self.mut_rate:
            vt = xgenotype.vt + random.uniform(-0.05,0.05)
        else:
            vt = xgenotype.vt
        # generate new genotype
        new_genotype = _genotype.Genotype(ut=ut, lt=lt, vt=vt, W=wx, V=vx)
        self.genotypes.append(new_genotype)


    def breed(self, parents):
        overall_ft = sum([gf[0] for gf in parents])
        # choose 2 individuals through roulette type selection
        while len(self.genotypes) < self.n_groups:
            pxs = []
            for xparent in range(2):
                acum = 0
                rsel = random.uniform(0,overall_ft)
                for px in parents:
                    acum += px[0]
                    if rsel <= acum:
                        # append genotype
                        pxs.append(px[1])
                        break
            # crossover
            p1w = pxs[0].W
            p2w = pxs[1].W
            p1v = pxs[0].V
            p2v = pxs[1].V
            k1 = np.random.randint(1,len(p1w)/2)
            k2 = np.random.randint(len(p1w)/2,len(p1w))
            wx1 = np.concatenate((p1w.flatten()[:k1],p2w.flatten()[k1:k2],p1w.flatten()[k2:]))
            wx2 = np.concatenate((p2w.flatten()[:k1],p1w.flatten()[k1:k2],p2w.flatten()[k2:]))
            wx1 = wx1.reshape(p1w.shape)
            wx2 = wx2.reshape(p2w.shape)
            # veto connections
            vx1 = np.concatenate((p1v.flatten()[:k1],p2v.flatten()[k1:k2],p1v.flatten()[k2:]))
            vx2 = np.concatenate((p2v.flatten()[:k1],p1v.flatten()[k1:k2],p2v.flatten()[k2:]))
            vx1 = vx1.reshape(p1v.shape)
            vx2 = vx2.reshape(p2v.shape)
            # new genotypes
            new_genotype1 = _genotype.Genotype(W=wx1, V=vx1)
            new_genotype2 = _genotype.Genotype(W=wx2, V=vx2)
            # 50% chance of mutations for each
            for gx in [new_genotype1, new_genotype2]:
                mx = np.random.randint(0,2)
                if mx:
                    self.mutate(gx)
                else:
                    self.genotypes.append(gx)
            # for non even number of groups
            if len(self.genotypes) > self.n_groups:
                self.genotypes = self.genotypes[:self.n_groups]

def save_obj(obj, filename="ea_exp"):
    # save into pickle
    save = False
    i = 1
    while save is not True:
        i_filename = "{}_agents{}_groups{}_gens{}_v{}.obj".format(filename, obj.n_agents, obj.n_groups, obj.n_gen, i)
        i_path = os.path.join(os.getcwd(), i_filename)
        if os.path.isfile(i_path):
            i += 1
        else:
            with open(i_path, "wb") as exp_file:
                pickle.dump(obj, exp_file)
            print("\nObject saved at {}".format(i_path))
            save = True

# x = Evolve()
# save_obj(x)
# with open("ea_exp[i].obj", "rb") as ea_exp:
    # xobj = pickle.load(ea_exp)




























    #
