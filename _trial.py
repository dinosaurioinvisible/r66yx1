
import numpy as np
from tqdm import tqdm
import _world
import _agent
import _genotype

class Trial:
    def __init__(self, t=1000, genotype=None, n_agents=3, world=None, n_trees=10, n_walls=4):
        self.t = t
        self.genotype = genotype
        self.n_agents = n_agents
        self.world = world
        if self.world == None:
            self.world = _world.World(n_trees=n_trees, n_walls=n_walls)
        self.agents = []
        self.trial()

    def trial(self):
        # allocate agents
        self.allocate_agents()
        # run trial
        for ti in tqdm(range(self.t)):
            for ax in self.agents:
                # update sensors and nnet
                xagents = [ag for ag in self.agents if ag!=ax]
                ax.update_in(self.world.walls,self.world.trees,xagents)
                # compute location
                ax.move_fx()
            # update location
            for ax in self.agents:
                # agents in new locations
                xagents = [ag for ag in self.agents if ag!=ax]
                inner_walls = self.world.walls[4:]
                ax.update_location(self.world.bounds, inner_walls, self.world.trees, xagents)
            # get trees in vecinity for each agent
            ax_tx = []
            for ax in self.agents:
                ax_trees = ax.feed_fx(self.world.trees)
                ax_tx.append(ax_trees)
            # matrix agents/trees
            ax_tx = np.array(ax_tx)
            # total agents near each tree
            sum_ax_tx = sum(ax_tx)
            # feed according to location
            for i in range(len(self.agents)):
                # how many agents (relative to self) are there for each tree
                ag_ax_tx = ax_tx[i] * sum_ax_tx
                self.agents[i].update_energy(ag_ax_tx)

    def allocate_agents(self):
        while len(self.agents) < self.n_agents:
            # location
            add = True
            x = np.random.randint(10, self.world.xmax-10)
            y = np.random.randint(10, self.world.ymax-10)
            o = np.radians(np.random.randint(0,360))
            # genotype
            if self.genotype == None:
                self.genotype = _genotype.Genotype()
                print("generated new genotype")
            agent = _agent.Agent(x, y, o, self.genotype)
            # check for superpositions
            for tx in self.world.trees:
                if agent.area.intersects(tx.area):
                    add = False
                    break
            for wx in self.world.walls[4:]:
                if agent.area.intersects(wx.area):
                    add = False
                    break
            if add:
                self.agents.append(agent)
