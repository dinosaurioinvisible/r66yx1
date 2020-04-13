
import numpy as np
import genotype
import world
import world_animation
from tqdm import tqdm
import os

# for each generation
# 100 groups of 3 agents for 1000 timesteps (lifetime)
# compare fitness of groups
# check the best 3
# select the best group and breed

class GA():
    def __init__(self, n_gen=1, n_groups=3, n_pop=3, lifetime=500, mut_rate=0.2\
        , write=False, filename="ga_exp", animate=False, anim_step=10, anim_best=False):
        self.n_gen = n_gen
        self.n_groups = n_groups
        self.n_pop = n_pop
        self.lifetime = lifetime
        self.mut_rate = mut_rate
        # data
        self.best_e = 0
        self.best_cases = []
        # animation
        self.animate = animate
        self.anim_step = anim_step
        self.anim_best = anim_best
        # simulation
        self.genotype = None
        self.genotypes = []
        self.best_genotypes = []
        self.simulation()
        self.best_case_animation()
        # write data
        # self.write_data(filename)

    def initial_population(self):
        # for each group (clones)
        for ng in range(self.n_groups):
            initial_genotype = genotype.Genotype()
            self.genotypes.append(initial_genotype)

    def simulation(self):
        # initial conditions
        world_xmax = 250
        world_ymax = 250
        n_walls = 5
        n_trees = 10
        self.initial_population()
        # for each generation
        for n in range(self.n_gen):
            print("\ngeneration = {}/{}".format(n+1,self.n_gen))
            simworld = world.World()
            max_e = 0
            best_group = None
            # for each group (same world for all for each generation)
            for ng in range(self.n_groups):
                print("group: {}/{}".format(ng+1,self.n_groups))
                # new agents
                simworld.agents = []
                gen = self.genotypes[ng]
                simworld.allocate_agents(self.n_pop, gen)
                # lifetime simulation
                for t in tqdm(range(self.lifetime)):
                    simworld.update()
                # print results
                agents_e = [ag.energy for ag in simworld.agents]
                total_e = sum(agents_e)
                print("agents energy: {}, total = {}".format(agents_e,total_e))
                if total_e > max_e:
                    max_e = total_e
                    best_group = simworld.agents
                    print("new max = {}".format(max_e))

            # print best data
            print("\nbest agents:")
            for ag in best_group:
                print("agent energy = {}".format(ag.energy))
            print("total energy = {}".format(max_e))
            # store best data (all genotypes - clonal)
            self.genotype = best_group[0].genotype
            self.best_genotypes.append(self.genotype)
            # record best case, only if better than previous best
            if max_e > self.best_e:
                self.best_cases.append([max_e, self.genotype, simworld])
                self.best_e = max_e
                self.anim_best = True
            # animate
            if self.animate:
                # animate if better than previous best
                if self.anim_best:
                    world_animation.sim_animation(self.lifetime, [world_xmax,world_ymax], simworld.walls, simworld.trees, best_group)
                    self.anim_best = False
                # animate after some number of generations
                else:
                    if (n+1)%self.anim_step==0:
                        world_animation.sim_animation(self.lifetime, [world_xmax,world_ymax], simworld.walls, simworld.trees, best_group)

            # reproduce (create new groups, keep best)
            self.genotypes = [self.genotype]
            for ng in range(self.n_groups-1):
                # starting energy and sensors (keep for now)
                energy = self.genotype.energy
                r = self.genotype.r
                max_speed = self.genotype.max_speed
                feed_range = self.genotype.feed_range
                feed_rate = self.genotype.feed_rate
                olf_angle = self.genotype.olf_angle
                olf_range = self.genotype.olf_range
                ir_angle = self.genotype.ir_angle
                ray_length = self.genotype.ray_length
                beam_spread = self.genotype.beam_spread
                aud_angle = self.genotype.aud_angle
                aud_range = self.genotype.aud_range
                # inputs and outputs (keep for now)
                n_in = self.genotype.n_in
                n_hidden = self.genotype.n_hidden
                n_out = self.genotype.n_out
                # thresholds
                ut = self.genotype.ut + np.random.randint(-1,2)*self.mut_rate
                lt = self.genotype.lt + np.random.randint(-1,2)*self.mut_rate
                vt = self.genotype.vt + np.random.randint(-1,2)*self.mut_rate
                # weights
                W = self.mut_weights(self.genotype.W)
                V = self.mut_weights(self.genotype.V)
                # plasticity #TODO
                plasticity = self.genotype.plasticity
                # create and save new genotype
                new_genotype = genotype.Genotype(energy, r, max_speed, feed_range, feed_rate, olf_angle, olf_range, ir_angle, ray_length, beam_spread, aud_angle, aud_range, n_in, n_hidden, n_out, ut, lt, vt, W, V, plasticity)
                self.genotypes.append(new_genotype)

    def mut_weights(self, weights):
        wf = weights.flatten()
        wfx = np.array([wij+np.random.randn() if np.random.randint(100)<100*self.mut_rate else wij for wij in wf])
        W = wfx.reshape(weights.shape)
        return W

    def best_case_animation(self):
        best_world = self.best_cases[-1][2]
        world_animation.sim_animation(self.lifetime, [best_world.xmax, best_world.ymax], best_world.walls, best_world.trees, best_world.agents)

    # def write_data(self, filename):
    #     # create file
    #     path = "/Users/sol/Desktop"
    #     path = os.path.join(path, self.filename)
    #     if not os.path.exists(path):
    #         os.makedirs(path)
    #     # create object
    #     data = []
    #     agents_data = 0
    #     ga_data = 0
    #     world_data = 0
    #     genotype_data = 0
    #     f = open("{}/".format())























































###
