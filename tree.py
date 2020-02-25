
import numpy as np

class Tree:
    def __init__(self, x=100, y=100, r=5, energy=100):
        # init
        self.x = x
        self.y = y
        self.r = r
        self.energy = energy
        self.data = []

    def update(self):
        self.energy += 1
        self.data.append(self.energy)

    def feeding_fx(self, feed_rate):
        e = 0
        if feed_rate <= self.energy:
            self.energy -= feed_rate
            e = feed_rate
        return e
