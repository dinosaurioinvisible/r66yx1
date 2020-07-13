
import numpy as np
import _world
import _agent
import _genotype
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon

class DebugTrial:
    def __init__(self, t=100, n_agents=2, genotype=None, world=None):
        self.t = t
        self.n_agents = n_agents
        self.agents = []
        if not genotype:
            self.create_debug_agents(genotype)
        if not world:
            self.world = _world.World(xmax=250,ymax=250,n_walls=0,n_trees=1,debug=True)
        self.define_debug_world()

    def create_debug_agents(self, genotype):
        for i in range(self.n_agents):
            x = 0
            y = 0
            o = 0
            agent = _agent.Agent(x,y,o,genotype)
            self.agents.append(agent)

    def define_debug_world(self):
        # walls
        w1 = _world.Wall(0,0,self.world.xmax,0)
        w2 = _world.Wall(0,0,0,self.world.ymax)
        w3 = _world.Wall(0,self.world.ymax,self.world.xmax,self.world.ymax)
        w4 = _world.Wall(self.world.xmax,0,self.world.xmax,self.world.ymax)
        self.world.walls = [w1,w2,w3,w4]

    def check_communication(self):
        a1 = self.agents[0]
        a2 = self.agents[1]
        for ti in range(self.t):
            # locations
            a1.x = 100
            a1.y = 100
            a1.o = np.radians(0)
            a2.x = 110
            a2.y = 100
            a2.o = np.radians(180)
            # trial
            #TODO



    def check_feeding(self):
        # create debug tree
        self.world.trees = []
        tx = 100
        ty = 100
        tr = 5
        debug_tree = _world.Tree(tx,ty,tr)
        self.world.trees.append(debug_tree)
        # check feeding
        print("\nfeeding test: x,y,o fixed")
        agent = self.agents[0]
        agent2 = self.agents[1]
        fr = agent.feeding_range
        for ti in range(self.t):
            agent.x = tx
            agent.y = (ty-tr)-(fr/2)
            agent.o = np.radians(90)
            agent2.x = tx+tr+1
            agent2.y = (ty+tr)+fr+10-ti
            agent2.o = np.radians(270)
            # pdb (check or change stuff)
            # import pdb; pdb.set_trace()
            # agent cicle
            for ax in self.agents:
                xagents = [ag for ag in self.agents if ag!=agent]
                ax.update_in(self.world.walls, self.world.trees, xagents)
            print("\nt={}".format(ti))
            print("vs1, vs2: {}".format(agent2.data.sm_info[-1][:2]))
            print("olf: {}".format(agent2.data.sm_info[-1][2]))
            print("energy: {}".format(agent2.data.sm_info[-1][3]))
            print("com signals: {}".format(agent.data.sm_info[-1][4:]))
            print("com signals: {}".format(agent2.data.sm_info[-1][4:]))
            # agent.move_fx()
            for ax in self.agents:
                # ax.update_location(self.world.bounds, self.world.walls, self.world.trees, xagents)
                ax.define_body_area()
                ax.define_feeding_area()
            # feeding
            ax_tx = []
            for ax in self.agents:
                ax_trees = ax.feed_fx(self.world.trees)
                ax_tx.append(ax_trees)
            sum_ax_tx = sum(ax_tx)
            for i in range(len(self.agents)):
                agent_ax_tx = ax_tx[i] * sum_ax_tx
                self.agents[i].update_energy(agent_ax_tx)
            print("ax_tx: {} > de: {}".format(agent_ax_tx, agent.data.de[-1]))






















#
