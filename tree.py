
import numpy as np

class Tree:
    def __init__(self, x=100, y=100, r=2, energy=100):
        # init
        self.x = x
        self.y = y
        self.r = r
        self.energy = energy

    def update(self):
        self.energy += 1

    def feeding_fx(self, agent=None):
        e = 0
        if agent:
            if agent.feed_rate <= self.energy:
                self.energy -= agent.feed_rate
                e = agent.feed_rate
        return e
