
import numpy as np
import genotype
import world
import world_animation
from tqdm import tqdm

# for each generation
# 100 groups of 3 agents for 1000 timesteps (lifetime)
# compare fitness of groups
# check the best 3
# select the best group and breed

class GA():
    def __init__(self, n_gen=255, n_groups=5, n_pop=3, lifetime=100, mut_rate=0.2, anim_step=50):
        self.n_gen = n_gen
        self.n_groups = n_groups
        self.n_pop = n_pop
        self.lifetime = lifetime
        self.mut_rate = mut_rate
        self.anim_step = anim_step
        # simulation
        self.genotype = None
        self.genotypes = []
        self.best_genotypes = []
        self.simdata = []
        self.simulation()

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
            # for each group (same world for each generation)
            print("\ngeneration = {}/{}".format(n+1,self.n_gen))
            simworld = world.World()
            max_e = 0
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
                    best_sim = simworld
                    print("new max = {}".format(max_e))
            # print best data and animate
            print("\nbest agents:")
            for ag in best_sim.agents:
                print("agent energy = {}".format(ag.energy))
            print("total energy = {}".format(max_e))
            if (n+1)/self.anim_step==0:
                world_animation.sim_animation([world_xmax,world_ymax], best_sim.walls, best_sim.trees, best_sim.agents)
            # store data (clonal)
            self.genotype = best_sim.agents[0].genotype
            self.best_genotypes.append(self.genotype)
            self.simdata.append(best_sim)
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
                n_rays = self.genotype.n_rays
                beam_spread = self.genotype.beam_spread
                aud_angle = self.genotype.aud_angle
                aud_range = self.genotype.aud_range
                # inputs and outputs (keep for now)
                n_in = self.genotype.n_in
                n_out = self.genotype.n_out
                # hidden units
                n_hidden = self.genotype.n_hidden
                # thresholds
                ut = self.genotype.ut + np.random.randint(-1,2)*self.mut_rate
                lt = self.genotype.lt + np.random.randint(-1,2)*self.mut_rate
                vt = self.genotype.vt + np.random.randint(-1,2)*self.mut_rate
                # weights
                W = self.mut_weights(self.genotype.W)
                V = self.mut_weights(self.genotype.V)
                # create new genotype
                new_genotype = genotype.Genotype(energy, r, max_speed, feed_range, feed_rate, olf_angle, olf_range, ir_angle, ray_length, n_rays, beam_spread, aud_angle, aud_range, n_in, n_hidden, n_out, ut, lt, vt, W, V)
                self.genotypes.append(new_genotype)
        return self.simdata

    def mut_weights(self, weights):
        wf = weights.flatten()
        wfx = np.array([wij+np.random.randn() if np.random.randint(100)<100*self.mut_rate else wij for wij in wf])
        W = wfx.reshape(weights.shape)
        return W























































###
