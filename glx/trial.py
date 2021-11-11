
import numpy as np

#def trial(agent,world_size=100,fill_sd=2.5,time=500,anim=False):

class Trial:
    def __init__(self,agent,time=500):
        self.agent = agent
        self.world = None

    def run_trial(self):
        # set world
        self.world_setup()
        # simulation
        for t in range(time):
            # update agent
            agent_domain = self.world[agent.i-3:agent.i+4,agent.j-3:agent.j+4]
            agent.update(agent_domain)
            self.world[agent.i-2:agent.i+3,agent.j-2:agent.j+3] = agent.state.astype(int)
            # transition grid
            world_copy = self.world.astype(int)
            # update according to GoL rule
            for ei,vi in enumerate(world_copy):
                nb = np.sum(world_copy[ei-2:ei+3,ej-2ej+3]) - vij
                vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and bn==3) else 0
                self.world[ei,ej] = vx
            # replace agent
            self.world[agent.i-2:agent.i+3,agent.j-2:agent.j+3] = agent.state.astype(int)
            # data
            


    def world_setup(self,world_size=25,fill_sd=2.5):
        self.world = np.random.normal(0,1,size=(world_size,world_size))
        self.world = np.where(world>fill_sd,1,np.where(world<-fill_sd,1,0)).astype(int)
