
from collections import defaultdict
import numpy as np
from glx_cell import Cell


'''the glider class: a collection of cells'''
class Glider:
    def __init__(self,gt,config,x0=50,y0=50):
        # group of cells "making" the glider
        self.cells={}
        self.state=[]
        # x0,y0 = center of the 3x3 glider's core
        self.define_glider(gt,config,x0,y0,canon=False)

    '''the update of the individual cells'''
    def update(self,world):
        # reset state, add signals to signals from the world
        self.state=[]
        for ci in self.cells:
            cell = self.cells[ci]
            if cell.alive and cell.st>0:
                cx,cy=cell.xy
                world[cx,cy] += 1
        # update each cell
        for ci in self.cells:
            cell=self.cells[ci]
            cx,cy=cell.xy
            if cell.alive:
                # get info from the surrounding 3x3 space
                env_xy = self.xy_around(cx,cy)
                cenv = np.zeros((9))
                for ei,exy in enumerate(env_xy):
                    cenv[ei] = world[tuple(exy)]
                # North default perspective here
                cenv = cenv.reshape(3,3)
                cell.update(cenv)
            self.state.append([cell.ci,cell.xy[0],cell.xy[1],cell.o,cell.st,cell.alive])
        self.state=np.array(self.state)
        self.check_global()

    '''check global conditions on living cells
    a) not to overlap; b) not to be alone'''
    def check_global(self):
        # (a) check overlaps
        a,inv_ind,counts = np.unique(self.state[:,1:3],axis=0,return_inverse=True,return_counts=True)
        for rep in np.where(counts>1)[0]:
            ov_xy = np.where(inv_ind==rep)[0]
            for oi in ov_xy:
                self.cells[oi+1].alive=0
                self.state[oi][5]=0
        # (b) check isolation (adjacent cells<3)
        cells_xy=defaultdict(int)
        for cell_state in self.state:
            if cell_state[5]==True:
                cells_xy[cell_state[1],cell_state[2]] += 1
        for ci in self.cells:
            cell=self.cells[ci]
            if cell.alive:
                adj_cells=0
                cx,cy=cell.xy
                env_xy=self.xy_around(cx,cy)
                for exy in env_xy:
                    adj_cells += cells_xy[tuple(exy)]
                # 4 = 3 other + self
                if adj_cells<4:
                    cell.alive=0
                    self.state[ci-1][5]=0

    '''helper fx to avoid doing this a lot of times'''
    def xy_around(self,x,y,r=1):
        axy = []
        for j in range(r,(-r-1),-1):
            for i in range(-r,(r+1)):
                axy.append([x+i,y+j])
        return np.asarray(axy)


    '''define as 1 of the 4 known canonical glider configurations'''
    def define_glider(self,gt,config,x0,y0,canon=False):
        # for the fully determined glider
        if canon:
            canon_sts=self.determined_glider(gt,config,x0,y0)
        # for random choice
        if config==0:
            config=np.random.randint(1,5)
        # given from the GoL classic glider
        if config==1:
            # c1: g1->g2, South=2
            core_act=[2,6,7,8,9]
            memb_xact=[10,14,25]
            orientation=2
        elif config==2:
            # c2: g2->g3: ? (assume same from g1->g2)
            core_act=[1,3,5,6,8]
            memb_xact=[18,22,23]
            orientation=2
        elif config==3:
            # c3: g3->g4: East=1
            core_act=[3,4,6,8,9]
            memb_xact=[10,11,22]
            orientation=1
        elif config==4:
            # g4->g1: ? (assume same from g3->g4)
            core_act=[1,5,6,7,8]
            memb_xact=[13,14,18]
            orientation=1
        else:
            print(cfg)
            raise("invalid starting configuration")
        # define cells
        n_cells = len(gt)
        cells_ci=[10,11,12,13,14,25,1,2,3,15,24,4,5,6,16,23,7,8,9,17,22,21,20,19,18]
        cells_xy = self.xy_around(x0,y0,2)
        for ci in range(1,n_cells+1):
            # define id, location, firing state, orientation and genotype
            ci_xy_index = np.where(np.asarray(cells_ci)==ci)[0][0]
            cx,cy = cells_xy[ci_xy_index]
            if ci in core_act:
                cst=1
            elif ci in memb_xact:
                cst=np.random.randint(0,2)
            else:
                cst=0
            co=orientation
            cst = 1 if ci in core_act else 0
            cgt=gt[ci]
            # for the known canonical sts
            if canon:
                for rx in canon_sts[ci-1]:
                    for ri in rx[0]:
                        cgt[ri]=rx[1]
            # add to the internal data structures
            self.cells[ci] = Cell(ci,cx,cy,co,cst,cgt)
            self.state.append([ci,cx,cy,co,cst,1])
        self.state = np.array(self.state)

    '''fully determined organized canonical glider'''
    def determined_glider(self,gt,config,x0,y0):
        # (for theta: +1=+90 (clockwise), -1=-90 (counter clockwise))
        # to fit with the np.rot90 so that:
        # 0:North, 1:East, 2:South, 3:West
        # c1: 32>1,1,0 - 272>0,0,-1 - 8>1,1,0 - 80>0,0,+1
        c1=[[[32],[1,1,0]],[[272],[0,0,-1]],[[8],[1,1,0]],[[80],[0,0,1]]]
        # c2: 272>1,0,0 - 424>0,0,-1 - 193>1,0,0 - 74>0,1,+1
        c2=[[[272],(1,0,0)],[[424],(0,0,-1)],[[193],(1,0,0)],[[74],(0,1,1)]]
        # c3: 136,(140)>1,1,0 - 208>0,1,-1 - 24>1,0,0 - 9>0,0,+1
        c3=[[[136,140],(1,1,0)],[[208],(0,1,-1)],[[24],(1,0,0)],[[9],(0,0,1)]]
        # c4: 388,(389)>1,0,0 - 290,(354)>0,1,-1 - 80>1,0,0 - 232>0,0,+1
        c4=[[[388,389],(1,0,0)],[[290,354],(0,1,-1)],[[80],(1,0,0)],[[232],(0,0,1)]]
        # c5: 482>1,1,0 - 181>0,0,-1 - 458>1,1,0 - 157>0,0,+1
        c5=[[[482],(1,1,0)],[[181],(0,0,-1)],[[458],(1,1,0)],[[157],(0,0,1)]]
        # c6: 209>1,1,0 - 90>0,1,-1 - 57>1,1,0 - 19>0,1,+1
        c6=[[[209],(1,1,0)],[[90],(0,1,-1)],[[57],(1,1,0)],[[19],(0,1,1)]]
        # c7: 48>1,0,0 - 36,(100,108,44)>0,0,-1 - 160,(161)>1,1,0 - 400>0,1,+1
        c7=[[[48],(1,0,0)],[[36,100,108,44],(0,0,-1)],[[160,161],(1,1,0)],[[400],(0,1,1)]]
        # c8: 60>1,1,0 - 22>0,1,-1 - 404>1,1,0 - 306>0,1,+1
        c8=[[[60],(1,1,0)],[[22],(0,1,-1)],[[404],(1,1,0)],[[306],(0,1,1)]]
        # c9: 26>1,0,0 - 11,(267)>0,1,-1 - 50>1,0,0 - 38,(102)>0,1,+1
        c9=[[[26],(1,0,0)],[[11,267],(0,1,-1)],[[50],(1,0,0)],[[38,102],(0,1,1)]]
        # c10*: 0,(16)>1,0,0 - 256>0,0,-1 - 0,(16)>1,0,0 - 64>0,0,+1
        c10=[]
        # c11*: 256>1,0,0 - 128>0,0,-1 - 0,(16,18)>1,0,0 - 8>0,0,+1
        c11=[]
        # c12: 128>1,0,0 - 320>0,0,-1 - 64>1,0,0 - 1,(129)>0,0,+1
        c12=[]
        # c13**C: 64,(96)>1,0,0 - 128>0,0,-1 - 8>1,0,0 - 0,(@128@,144,16)>0,0,+1
        # at g41, if c14=1 => c13=1 (same as c23)
        # c13: 64, (96)>1,0,0 - 128>0,0,-1 - 8>1,0,+1 - 0,(32)>0,0,0
        # solved by moving and reorienting at g34 (like c18,c23)
        c13=[]
        # c14**B: 0,(@16@)>1,0,0 - 64>0,0,-1 - 1>1,*1*,0 - @0@,(16,18,2)>0,0,+1
        # 0 and 16 appear in g12 and g41, but they must exclusive
        # the only way to distinguish g12 and g14 is through self activation
        # ?
        c14=[]
        # c15: 64,(66)>1,0,0 - 72>0,0,-1 - 3>1,0,0 - 1,(33,37,5)>0,0,+1
        c15=[]
        # c16: 72>1,0,0 - 9>0,0,-1 - 7>1,0,0 - 2>0,0,+1
        c16=[]
        # c17: 9>1,0,0 - 1,(129)>0,0,-1 - 6>1,0,0 - 4,(12)>0,0,+1
        c17=[]
        # c18**C: 1>1,0,0 - 0,(@16@)>0,0,-1 - 4>1,*1*,0 - @0@,(16)>0,0,+1
        # c18: 1>1,0,-1 - 0>0,0,0 - 4>1,0,+1 - 0>0,0,0
        # solved by changing orientation and move at the sime time-step (like c13,c23)
        c18=[]
        # c19: 3>1,0,0 - 1,(33)>0,0,-1 - 36>1,0,0 - 4,(132)>0,0,+1
        c19=[]
        # c20: 7>1,0,0 - 2>0,0,-1 - 288>1,0,0 - 36>0,0,+1
        c20=[]
        # c21: 6>1,0,0 - 4,(12,13,5)>0,0,-1 - 256,(258)>1,0,0 - 288>0,0,+1
        c21=[]
        # c22**B: 4>1,0,0 - 0,(@16@,18,2)>0,0,-1 - @0@,(16)>1,0,0 - 256>0,0,+1
        # same as c14: 2 different transitions with no input
        # ?
        c22=[]
        # c23**C: 32>1,0,0 - 0,(16,144,@128@)>0,0,-1 - 256,(264)>1,0,0 - 128>0,0,+1
        # at g23, if c22=1 => c23=1 (same as c13)
        # c23: 32>1,0,-1 - 0,(16,24,8)>0,0,0 - 256,(264)>1,0,0 - 128>0,0,+1
        # solved by moving and reorienting at g12 (like c13,c18)
        c23=[]
        # c24: 256,(258)>1,0,0 - 4,(132)>0,0,-1 - 128>1,0,0 - 320>0,0,+1
        c24=[]
        # c25*: 0,(16,18,2)>1,0,0 - 32>0,0,-1 - 64,(320,352,96)>1,0,0 - 128>0,0,+1
        c25=[]
        # the list of canonical states and transitions
        return [c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24,c25]


























#
