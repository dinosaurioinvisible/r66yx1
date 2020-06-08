
import numpy as np
import _world
import _agent
import _genotype

class Trial:
    def __init__(self, t=100, n_agents=1):
        self.t = t
        self.n_agents = n_agents
        self.world = _world.World()
        self.agents = []
        self.allocate_agents()

    def trial(self):
        for ti in range(self.t):
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
                world_objects = self.world.walls+self.world.trees+xagents
                ax.update_location(world_objects)
            # feed according to location
            ax_tx = []
            for ax in self.agents:
                ax_trees = ax.feed_fx(self.world.trees)
                ax_tx.append(ax_trees)
            sum_ax_tx = [0]*len(self.world.trees)
            for a in range(len(ax_tx)):
                for i in range(len(ax_tx)):
                    sum_ax_tx[i] += ax_tx[a][i]
            for a in range(len(self.agents)):
                tx_agent = [sum_ax_tx[i]*ax_tx[a][i] for i in range(len(sum_ax_tx))]
                self.agents[a].update_energy(tx_agent)
        return self.t, self.world, self.agents


    def allocate_agents(self):
        while len(self.agents) < self.n_agents:
            add = True
            x = np.random.randint(10, self.world.xmax-10)
            y = np.random.randint(10, self.world.ymax-10)
            o = np.radians(np.random.randint(0,360))
            agent = _agent.Agent(x, y, o, _genotype.Genotype())
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
