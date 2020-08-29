
import numpy as np
from tqdm import tqdm
import _world
import min_agent


class Trial:
    def __init__(self, genotypes
        , mode="normal"
        , t=1000
        , world=None
        , n_trees=10
        , world_size=500
        , n_walls=4):

        self.t = t
        # ga or minimal trials
        if mode == "minimal":
            self.genotypes = [genotypes[0]]
            self.world = _world.World(xmax=100, ymax=100, n_trees=1, n_walls=4)
        else:
            self.genotypes = genotypes
            self.world = _world.World(xmax=world_size, ymax=world_size, n_trees=n_trees, n_walls=n_walls)
        self.agents = []
        self.allocate_agents()
        self.run_trial()

    def run_trial(self):
        for ti in tqdm(range(self.t)):
            for ax in self.agents:
                # if alive
                if ax.e > 0:
                    # update sensors and nnet
                    xagents = [ag for ag in self.agents if ag!=ax]
                    ax.update_in(self.world.walls,self.world.trees,xagents)
                    # compute new location
                    ax.move_fx()
                else:
                    ax.data.fill_off()
            # update location
            for ax in self.agents:
                if ax.e > 0:
                    xagents = [ag for ag in self.agents if ag!=ax]
                    inner_walls = self.world.walls[4:]
                    ax.update_location(self.world.bounds, inner_walls, self.world.trees, xagents)
            # update energy simple version
            for ax in self.agents:
                if ax.e > 0:
                    ax.update_e(self.world.trees)
            # # get trees in vecinity for each agent
            # ax_tx = []
            # for ax in self.agents:
            #     # list of trees (1: True, 0: False)
            #     ax_trees = np.array([0]*len(self.world.trees))
            #     if ax.e > 0:
            #         ax_trees = ax.feed_fx(self.world.trees)
            #     ax_tx.append(ax_trees)
            # # matrix agents/trees
            # ax_tx = np.array(ax_tx)
            # # total agents near each tree
            # sum_ax_tx = sum(ax_tx)
            # # feed according to location
            # for i in range(len(self.agents)):
            #     # how many agents (relative to self) are there for each tree
            #     if self.agents[i].e > 0:
            #         ag_ax_tx = ax_tx[i] * sum_ax_tx
            #         self.agents[i].update_energy(ag_ax_tx)

    def allocate_agents(self):
        # allocate
        n = 0
        while len(self.agents) < len(self.genotypes):
            add = True
            x = np.random.randint(10, self.world.xmax-10)
            y = np.random.randint(10, self.world.ymax-10)
            o = np.radians(np.random.randint(0,360))
            agent = min_agent.Agent(self.genotypes[n], x, y, o)
            # check for superpositions
            for tx in self.world.trees:
                if agent.area.intersects(tx.area):
                    add = False
                    break
            for wx in self.world.walls[4:]:
                if agent.area.intersects(wx.area):
                    add = False
                    break
            xagents = [ag for ag in self.agents if ag!=agent]
            for ax in xagents:
                if agent.area.intersects(ax.area):
                    add = False
                    break
            if add:
                self.agents.append(agent)
                n += 1























##
