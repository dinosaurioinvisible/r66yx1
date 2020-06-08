
import numpy as np
import simgenotype
import simworld
import simanimation
from tqdm import tqdm
import os

# TODO aclonal approach?

class GA():
    def __init__(self, n_gen=2, n_groups=5, n_agents=3\
        , lifetime=500\
        , mut_rate=0.1\
        , clonal=True\
        , xmax=250, ymax=250, n_walls=5, n_trees=5\
        , anim_best=False, anim_step=False\
        , write=False, filename="ga_exp"):
        # groups of agents
        self.n_gen = n_gen
        self.n_groups = n_groups
        self.n_agents = n_agents
        self.lifetime = lifetime
        self.mut_rate = mut_rate
        # world
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        # data
        self.best_e = 0
        self.best_cases = []
        # animation
        self.anim_best = anim_best
        self.anim_step = anim_step
        # simulation
        self.genotype = None
        self.genotypes = []
        self.best_genotypes = []
        # do
        self.simulation()
        self.best_case_animation()
        self.write_data(write, filename)


    def initial_population(self):
        # for each group (clones)
        for group in range(self.n_groups):
            group_initial_genotype = simgenotype.Genotype()
            self.genotypes.append(group_initial_genotype)

    def simulation(self):
        # initial genotypes (clonal but different for each group)
        self.initial_population()
        # for each generation: create world
        for n in range(self.n_gen):
            print("\ngeneration = {}/{}".format(n+1, self.n_gen))
            world = simworld.World(self.xmax, self.ymax, self.n_walls, self.n_trees)
            best_e = 0
            best_group = None
            # for each group (same world for all for each group in the same generation)
            for ng in range(self.n_groups):
                print("group: {}/{}".format(ng+1,self.n_groups))
                # create new agents and introduce them in the simworld
                genotype = self.genotypes[ng]
                world.allocate_agents(self.n_agents, genotype)
                # simulate group lifetime
                for tx in tqdm(range(self.lifetime)):
                    world.update()
                # get and print results
                agents_e = [ag.energy for ag in world.agents]
                av_e = sum(agents_e)/len(world.agents)
                print("agents energy: {}, average = {}".format(agents_e,av_e))
                # save if best
                if av_e > best_e:
                    best_e = av_e
                    best_group = world.agents
                    print("new best = {}".format(best_e))
                # reset world for next group
                world.reset()
            # print best data for past generation
            print("\nbest agents:")
            for ag in best_group:
                print("agent energy = {}".format(ag.energy))
            print("average energy = {}".format(best_e))
            # check and save if better than previous best (all generations)
            if best_e > self.best_e:
                self.best_cases.append([best_e, best_group, world])
                self.best_e = best_e
                print("best over all generations")
                if self.anim_best:
                    simanimation.world_animation(self.lifetime, best_group, world)
            # animation for fixed steps
            if self.anim_step:
                if (n+1)%self.anim_step==0:
                    simanimation.world_animation(self.lifetime, best_group, world)

            # breeding
            best_genotype = best_group[0].genotype
            # copy the identic best genotype for one group
            self.genotypes = [best_genotype]
            for ng in range(self.n_groups-1):
                # mutation of the nnet only for now
                # thresholds
                ut = best_genotype.ut + np.random.randint(-1,2)*self.mut_rate
                lt = best_genotype.lt + np.random.randint(-1,2)*self.mut_rate
                vt = best_genotype.vt + np.random.randint(-1,2)*self.mut_rate
                # weights
                W = self.mut_weights(best_genotype.W)
                V = self.mut_weights(best_genotype.V)
                # create and save new genotype
                new_genotype = simgenotype.Genotype(ut=ut, lt=lt, vt=vt, W=W, V=V)
                self.genotypes.append(new_genotype)


    def mut_weights(self, weights):
        wf = weights.flatten()
        wfx = np.array([wij+np.random.randn() if np.random.randint(100)<100*self.mut_rate else wij for wij in wf])
        W = wfx.reshape(weights.shape)
        return W

    def best_case_animation(self):
        best_world = self.best_cases[-1][2]
        best_agents = self.best_cases[-1][1]
        simanimation.world_animation(self.lifetime, best_agents, best_world)

    def write_data(self, write, filename):
        if write:
            pass
























    #
