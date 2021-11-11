
import numpy as np
from collections import defaultdict



class BasicMembraneAgent:
    def __init__(self,i,j,genotype,st0):
        self.i,self.j = i,j
        self.genotype = genotype
        self.setup(st0)

    def setup(self,st0):
        self.core =






class MixedAgent:
    def __init__(self,i,j,core_gt,memb_gt,st0):
        self.i,self.j = i,j
        self.core_gt = core_gt
        self.memb_gt = memb_gt
        self.state = state

    def update(self,agent_domain):
        core = get_core(agent_domain)
        membrane = get_membrane(agent_domain)



# Simple matrix of fixed transitions
class BasicAgentCore:
    def __init__(self,i,j,genotype,st0):
        self.i,self.j = i,j
        self.genotype = genotype
        self.state = st0
        self.data = []

    def update(self,core_domain):
        env = layer2int(core_domain)
        current_st = matrix2int(self.state)
        new_st = self.genotype[current_st][env]
        self.data.append([current_st,env,new_st])
        self.state = int2matrix(new_st)

# Membrane updates core, but get updated by GoL rules
class BasicAgentMembrane:
    def __init__(self,i,j,genotype,st0,core_st0):
        self.i,self.j = i,j
        self.genotype = genotype
        self.st = st0
        self.core_st = core_st0
        self.data = []

    def update(self,membrane_domain):
        env = layer2int(membrane_domain)
        current_core_st = matrix2int(self.core_st)
        new_core_st = self.genotype[current_core_st][env]





class Core:
    def __init__(self,i,j,zells,st0):
        self.i,self.j = i,j
        self.zells = self.zells
        self.rel_pos = xy_around(i,j)
        self.state = st0

    def update(self,core_domain):
        for zell in zells:
            zell_domain = core_domain[self.i-]

        for zell in zells:
            zell_domain = core_domain[]
            zell.update(zell_domain)

    def setup_zells(self):
        for zi in range(3):
            for zj in range(3):


class Zell:
    def __init__(self,i,j,genotype,st0):
        self.i,self.j = i,j
        self.genotype = genotype
        self.state = st0

    def update(self,zell_domain):
        env_in = arr2int(zell_domain)
        self.state = self.genotype[env_in]
