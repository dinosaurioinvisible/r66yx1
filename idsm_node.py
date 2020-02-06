
class Node:
    def __init__(self, position, velocity, weight, t2a):
        self.position = position
        self.velocity = velocity
        self.weight = 0
        self.t2a = 10
        self.active = False

    def activation_fx(self):
        if self.t2a > 0:
            self.t2a -= 1
        else:
            self.active = True
