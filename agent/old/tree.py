
import numpy as np

class Tree:
    def __init__(self, x=100, y=100, r=5, energy=2500):
        # init
        self.x = x
        self.y = y
        self.r = r
        self.energy = energy
        self.data = []

    def update(self):
        self.energy += 1
        self.data.append(self.energy)

    def feeding_fx(self, feed_rate, other_agents):
        e = 0
        n_agents = 1
        for agent in other_agents:
            dist = np.linalg.norm(np.array([self.x,self.y])-np.array([agent.x,agent.y])) - agent.r - self.r
            if dist <= agent.feed_range:
                n_agents += 1
        if feed_rate <= self.energy:
            e = feed_rate**n_agents
            self.energy -= e
        return e
