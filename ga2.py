
import numpy as np
import genotype
import world

class GA():
    def __init__(self, n_gen=100, n_pop=3, lifetime=100, mut_rate=0.2):
        self.n_gen = n_gen
        self.n_pop = n_pop
        self.lifetime = lifetime
        self.mut_rate = mut_rate
        # data
        self.simdata = []
        self.genotypes = []
        self.initial_population()
        self.simulation()

    def initial_population(self):
        for n in self.n_pop:
            self.genotypes.append(genotype.Genotype())

    def simulation(self):
        world_xmax = 250
        world_ymax = 250
        n_walls = 5
        n_trees = 10
        # for each generation
        for n in range(self.n_gen):
            simworld = world.World(world_xmax, world_ymax, n_walls, n_trees, self.genotypes)
            # for each timestep within lifetime of generations
            for t in range(self.lifetime):
                simworld.update()
            # world_data = [[simworld.xmax, simworld.ymax], simworld.walls[4:], simworld.trees, simworld.agents]
            # sort parents (by energy) and select
            parents = sorted(simworld.agents, reverse=True, key=lambda agent:agent.energy)




























































###
