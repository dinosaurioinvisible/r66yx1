
import numpy as np
import _genotype
import _trial
import _trial_animation
import random
from copy import deepcopy
import pickle
import time
import os


class Evolve():
    def __init__(self, n_gen=100, n_groups=10, n_trials=10\
        , genotype=None\
        , n_agents=1\
        , n_trees=10\
        , trial_t=1000\
        , mut_rate=0.1\
        , anim=False\
        , alarm=False\
        , save=10):
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
        self.alarm = alarm
        self.save = save
        # opt load genotype
        if not genotype:
            self.genotypes = [_genotype.Genotype() for i in range(self.n_groups)]
        else:
            self.genotypes = [genotype for i in range(self.n_groups)]
        # for saving cases (create temp file)
        self.good_cases = []
        self.index = "{:04}".format(int([i for i in os.listdir() if "temp" in i][-1].split("_")[1])+1)
        self.description = "{}v{}o{}e{}c".format(self.genotypes[0].vs_n,self.genotypes[0].olf_n,self.genotypes[0].e_in,self.genotypes[0].com_len)
        self.save_sim(filename="temp")
        # run
        self.simulation()


    def simulation(self):
        # for each generation
        for n in range(self.n_gen):
            print("\n")
            groups_data = []
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
                    # NOTE: fitnness fx
                    # regarding energy
                    ff_e = np.array([ag.e for ag in xtrial.agents])
                    ff_ags_e = sum(ff_e) * sum(np.where(ff_e>0, 1, ff_e))/self.n_agents
                    # regarding trees
                    ff_tcount = sum([sum(sum(ag.data.agent_ax_tx)) for ag in xtrial.agents])/(self.n_agents*self.trial_t)
                    ff_trees = ff_tcount*(1+n_trees)/n_trees
                    # fitness
                    ft = ff_ags_e * ff_trees
                    group_fts.append(ft)
                    for i in range(len(ff_e)):
                        print("agent{} energy: {}".format(i+1, round(ff_e[i],2)))
                    print("group fitness: {}".format(round(group_fts[-1],2)))
                # weight trial performances for group
                sorted_fts = sorted(group_fts, reverse=True)
                ft_sum = 0
                for i in range(self.n_trials):
                    # NOTE: sorted fts ???
                    ft_sum += (i+1)*group_fts[i]
                w_ft = 2/(self.n_trials*(self.n_trials+1)) * ft_sum
                # save group data
                groups_data.append([w_ft, xtrial.genotype])

            # print info for generation and get best group
            print("\ngeneration groups results:")
            for gi in range(len(groups_data)):
                print("group {} fitness: {}".format(gi+1,round(groups_data[gi][0],2)))
            sorted_groups = sorted(groups_data, key=lambda x:x[0], reverse=True)
            best_group = sorted_groups[0]
            print("best group weighted fitness: {}".format(round(best_group[0],2)))
            # save
            self.good_cases.append([n, best_group[0], best_group[1]])
            best_cases = sorted(self.good_cases, key=lambda x:x[1], reverse=True)[:5]
            print("\nbest cases until now:")
            for bc in best_cases:
                print("generation: {}, fitness: {}".format(bc[0],round(bc[1],2)))
            # for debugging
            # os.system("osascript -e \"set Volume 10\" ")
            # os.system("open -a vlc ~/desktop/hadouken.mp4")
            # _trial_animation.sim_animation(xtrial.world, xtrial.agents, self.trial_t)
            # import pdb; pdb.set_trace()
            # animation
            if self.anim:
                _trial_animation.sim_animation(xtrial.world, xtrial.agents, self.trial_t)
            # save temp
            if len(self.good_cases)%self.save==0:
                # index (assuming ordered sequence in dir)
                self.save_sim(filename="temp")

            #NOTE: genetic selection
            # reset genotypes for new generation
            self.genotypes = []
            # best genotype replication (egoistical approach)
            self.genotypes.append(deepcopy(best_group[1]))
            # best genotype mutations (half-1 of new generation)
            for ng in range(int(self.n_groups/2)-1):
                new = self.mutate(best_group[1])
                self.genotypes.append(new)
            # remaining new half (use only the best current half)
            parents = [i for i in sorted_groups if i[0] > 0]
            # in case there are no 2 parents (initial generations)
            if len(parents) < 2:
                parents = sorted_groups
            # breed through roulette type selection (pairs)
            while len(self.genotypes) < self.n_groups:
                new12 = self.breed(parents)
                self.genotypes.extend(new12)

        # save, alert and end
        self.save_sim(filename="good_cases")
        if self.alarm:
            try:
                os.system("osascript -e \"set Volume 3\" ")
                os.system("open -a vlc ~/desktop/brigth-engelberts-free-me-now.mp3")
                # os.system("open -a vlc ~/desktop/hadouken.mp4")
            except:
                pass

    def mutate(self, xgenotype):
        # connectivity weights
        wx = xgenotype.W
        # for every weight, if within mut rate, mutate from [-0.1, 0.1]
        for i in range(len(wx)):
            for j in range(len(wx[i])):
                if np.random.uniform(0,1)<self.mut_rate:
                    # wx[i][j] = 1 if wx[i][j] == 0 else 0
                    wx[i][j] += np.random.uniform(-0.1,0.1)
        # check no w[i][j] goes out of [0,1]
        wx = np.where(wx<0, 0, wx)
        wx = np.where(wx>1, 1, wx)
        # veto weights
        vx = xgenotype.V
        for i in range(len(vx)):
            for j in range(len(vx[i])):
                if np.random.uniform(0,1)<self.mut_rate/2:
                    # vx[i][j] = 1 if vx[i][j] == 0 else 0
                    vx[i][j] += random.uniform(-0.1,0.1)
        vx = np.where(vx<0, 0, vx)
        vx = np.where(vx>1, 1, vx)
        # reset veto matrix
        v_reset=False
        if np.random.uniform(0,1)<self.mut_rate:
            v_reset = True
        # hidden units
        n_hidden = xgenotype.n_hidden
        if np.random.uniform(0,1)<self.mut_rate:
            n_hidden += np.random.choice([-1,1])
        n_hidden = 2 if n_hidden < 2 else n_hidden
        n_hidden = 6 if n_hidden > 6 else n_hidden
        # thresholds
        ut = xgenotype.ut
        if np.random.uniform(0,1)<self.mut_rate:
            ut = xgenotype.ut + random.uniform(-0.05,0.05)
        ut = np.random.uniform(0.5,1) if 0.5 < ut > 1 else ut
        lt = xgenotype.lt
        if np.random.uniform(0,1)<self.mut_rate:
            lt = xgenotype.lt + random.uniform(-0.05,0.05)
        lt = np.random.uniform(0,0.4) if 0 < lt > 0.4 else lt
        vt = xgenotype.vt
        if np.random.uniform(0,1)<self.mut_rate:
            vt = xgenotype.vt + random.uniform(-0.05,0.05)
        vt = np.random.uniform(0.8,1) if 0.6 < vt > 1 else vt
        # generate new genotype
        new_genotype = _genotype.Genotype(n_hidden=n_hidden, ut=ut, lt=lt, vt=vt, W=wx, V=vx, v_reset=v_reset)
        return new_genotype


    def breed(self, parents):
        overall_ft = sum([gf[0] for gf in parents])
        # choose 2 individuals through roulette type selection
        # while len(self.genotypes) < self.n_groups:
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
        # thresholds
        ut1 = pxs[0].ut
        ut2 = pxs[1].ut
        lt1 = pxs[0].lt
        lt2 = pxs[1].lt
        vt1 = pxs[0].vt
        vt2 = pxs[1].vt
        # hidden units
        n_hu1 = wx1.shape[0]-pxs[0].n_input-pxs[0].n_output
        n_hu2 = wx2.shape[0]-pxs[1].n_input-pxs[1].n_output
        # new genotypes
        new_genotypes = []
        new_genotype1 = _genotype.Genotype(n_hidden=n_hu1, ut=ut1, lt=lt1, vt=vt1, W=wx1, V=vx1)
        if np.random.choice((True,False)):
            new_genotype1 = self.mutate(new_genotype1)
        new_genotypes.append(new_genotype1)
        # for uneven groups
        if len(self.genotypes) < self.n_groups:
            new_genotype2 = _genotype.Genotype(n_hidden=n_hu2, ut=ut2, lt=lt2, vt=vt2, W=wx2, V=vx2)
            if np.random.choice((True,False)):
                new_genotype2 = self.mutate(new_genotype2)
            new_genotypes.append(new_genotype2)
        return new_genotypes


    def save_sim(self, dirname="objs", filename="temp"):
        # save into pickle
        save = False
        while save is not True:
            # look for previous temps
            idx = "{}_{}".format(filename,self.index)
            temps = [i for i in os.listdir() if idx in i]
            # filename
            i_filename = "{}_{}_agents{}_groups{}_gens{}_trials{}_t{}_cases{}.obj".format(idx, self.description, self.n_agents, self.n_groups, self.n_gen, self.n_trials, self.trial_t, len(self.good_cases))
            dirpath = os.path.join(os.getcwd(), dirname)
            i_path = os.path.join(dirpath, i_filename)
            if not os.path.isfile(i_path):
                # save
                with open(i_path, "wb") as exp_file:
                    pickle.dump(self.good_cases, exp_file)
                print("\n{} object saved at: \n{}".format(filename, i_path))
                # remove previous version
                for temp in temps:
                    os.remove(os.path.join(os.getcwd(),temp))
                    print("removed previous temporal file: \n{}".format(temp))
                save = True
            else:
                filename = "{}".format(time.ctime())

# for saving the whole simulation object, not just the good cases
def save_obj(obj, dirname="objs", filename="evolexp"):
    # save into pickle
    save = False
    i = 1
    while save is not True:
        i_filename = "{}_v{}.obj".format(filename, i)
        dirpath = os.path.join(os.getcwd(), dirname)
        i_path = os.path.join(dirpath, i_filename)
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
