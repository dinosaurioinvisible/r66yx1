
import numpy as np
from copy import deepcopy


'''class for the cell-elements composing the glider-system'''
class Cell:
    def __init__(self,ci,x,y,o,st,gt):
        # aliveness and id
        self.alive=1
        self.ci=ci
        # location in the CA grid
        self.xy=np.array([x,y])
        # st: pulse/signal emision or not
        self.st=st
        # o: 0=North, 1=East, 2=South, 3=West
        self.o=o
        # moving responses according to o
        self.mu=np.array([[0,1],[1,0],[0,-1],[-1,0]])
        # matrix for outputs
        self.u=gt
        # data save
        # self.data=CellData(self.xy,self.st,self.o)

    '''each cell should act according to their environmental info
    (spatially interpreted pulses/signals from neighborhood)
    > sensory domain: set of all possible input arrays
    > cognitive domain: set of paths mapping sensor/behav domains
    > behavioural domain: set of all possible output arrays
    response: [state:{1,0}, move:{1/0}, orientation:{0,1,2,3}]'''
    def update(self,cenv):
        # adjust env matrix according to orientation (clockwise)
        sx = np.rot90(cenv,self.o)
        # convert to binary to map to output
        bx = ''.join(str(int(i)) for i in sx.flatten())
        rx = int(bx,2)
        # check for response. If it isn't one, create
        if not rx in self.u:
            dxy = np.random.randint(0,2)
            dst = np.random.randint(0,2)
            do = np.random.randint(-1,2)
            self.u[rx] = [dxy,dst,do]
        # out: new location
        dxy = int(self.u[rx][0])
        self.xy += dxy*self.mu[int(self.o)]
        # out: new (signaling) state and orientation
        self.st = self.u[rx][1]
        # new theta, rearrange angle within range (just in case)
        self.o += self.u[rx][2]
        self.o = int(np.where(self.o>3,self.o-4, np.where(self.o<0,self.o+4,self.o)))
        # for analysis
        # self.data.save(env,sx,rx,self.xy,self.st,self.o)


'''class for saving cell states and in/out data at each t'''
class CellData:
    def __init__(self,xy,st,o):
        # initial states
        self.xy=xy
        self.st=st
        self.o=o
        # acting (init as -1 to show they are not active yet)
        self.env=np.array([-1]*9)
        self.sx=np.array([-1]*9)
        self.rx=np.array([-1])

    # should i use deepcopy here?
    def save(self,env,sx,rx,xy,st,o):
        self.env = np.vstack(self.env,env)
        self.sx = np.vstack(self.sx,sx)
        self.rx = np.vstack(self.rx,rx)
        # new states
        self.xy = np.vstack(self.xy,xy)
        self.st = np.vstack(self.st,st)
        self.o = np.vstack(self.o,o)


#
