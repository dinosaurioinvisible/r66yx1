
from collections import defaultdict
import numpy as np
from xcell import Cell


'''the glider class: a collection of cells'''
class Glider:
    def __init__(self,gt,config,x0=50,y0=50):
        # group of cells "making" the glider
        self.cells={}
        self.state=[]
        # x0,y0 = center of the 3x3 glider's core
        self.define_glider(x0,y0,gt,config)

    '''the update of the individual elements/cells, survival conditions:
    a) receive at least one pulse/signal/activation (not from itself..)
    b) not to overlap with other cells'''
    def update(self,world):
        # world: defauldict for active elements
        self.state=[]
        # add cell signals to world state
        for ci in self.cells:
            cell=self.cells[ci]
            if cell.alive and cell.st>0:
                cx,cy = cell.xy
                world[cx,cy] += 1
        # get input from cell surroundings and update
        for ci in self.cells:
            cell=self.cells[ci]
            if cell.alive:
                # surrounding 3x3 matrix
                x,y = cell.xy
                exy = self.xy_around(x,y)
                # external/default (North) perspective here
                cenv = np.zeros((9))
                for i in range(9):
                    ex,ey = exy[i]
                    cenv[i] = world[ex,ey]
                # update cell (condition (a) in cell)
                cenv = cenv.reshape(3,3)
                cell.update(cenv)
            self.state.append([cell.ci,cell.xy[0],cell.xy[1],cell.o,cell.st,cell.alive])
        self.state = np.array(self.state)
        # condition (b): get overlaps indices and deactivate cells
        a,inv_ind,counts = np.unique(self.state[:,1:3],axis=0,return_inverse=True,return_counts=True)
        for rep in np.where(counts>1)[0]:
            ois = np.where(inv_ind==rep)[0]
            for oi in ois:
                self.cells[oi+1].alive=0
                self.state[oi][5]=0

    '''to avoid doing this a lot of times'''
    def xy_around(self,x,y):
        axy = []
        for j in range(1,-2,-1):
            for i in range(-1,2):
                axy.append([x+i,y+j])
        return np.asarray(axy)

    '''define glider's "body"/space/domain,
    numeration is arbitrarily divided as:
    2201 to 2209 for the "core" cells,
    2210 to 2222 for the "membrane" cells'''
    def define_glider(self,x0,y0,gt,cfg):
        # get initial configuration for glider
        core_st,core_or,mcells = self.define_config(cfg)
        core_xy = self.xy_around(x0,y0)
        # glider's core (1:9)
        ci=1
        for xy in core_xy:
            cx,cy=xy
            co=core_or
            cst=core_st[ci]
            cgt=gt[ci]
            self.cells[ci] = Cell(ci,cx,cy,co,cst,cgt)
            self.state.append([ci,cx,cy,co,cst,1])
            ci+=1
        # glider's membrane (10:22)
        for ci in range(10,23):
            cst=0
            mcx,mcy,co = mcells[ci]
            cx = x0+mcx
            cy = y0+mcy
            cgt = gt[ci]
            cell = Cell(ci,cx,cy,co,cst,cgt)
            self.cells[ci] = cell
            self.state.append([ci,cx,cy,co,cst,1])
        self.state = np.array(self.state)

    '''select one of the 4 known canonical glider configurations:
    cc: core states: signaling states in the 3x3 inner space (1:9)
    co: core orientations: these cells move as a block
    mc: membrane locations and orientations (mci,mcx,mcy,mco)
    mc locs are to ensure the correspondence among cells
    membrane orientations don't follow those from the core
    (the orientations for transitions are just for init)'''
    def define_config(self,config):
        # for random choice
        if config==0:
            config=np.random.randint(1,5)
        # given from the GoL classic glider
        if config==1:
            # c1: g1->g2, South=2
            core_sts=[None, 0,1,0, 0,0,1, 1,1,1]
            core_or=2
            mcells=[[None,(10,2),(11,2),(12,2),None],[None,None,None,None,(13,0)],[(14,0),None,None,None,(15,0)],[(16,0),None,None,None,(17,0)],[(18,0),(19,2),(20,2),(21,2),(22,0)]]
        elif config==2:
            # c2: g2->g3: ? (assume same from g1->g2)
            core_sts=[None, 1,0,1, 0,1,1, 0,1,0]
            core_or=2
            mcells=[[(14,2),(10,1),(11,1),(12,1),(13,2)],[(16,2),None,None,None,(15,2)],[(18,2),None,None,None,(17,2)],[None,None,None,None,(22,2)],[None,(19,0),(20,0),(21,0),None]]
        elif config==3:
            # c3: g3->g4: East=1
            core_sts=[None, 0,0,1, 1,0,1, 0,1,1]
            core_or=1
            mcells=[[None,None,(10,3),(11,3),(12,3)],[(14,1),None,None,None,(13,1)],[(16,1),None,None,None,(15,1)],[(18,1),None,None,None,(17,1)],[None,(19,3),(20,3),(21,3),(22,3)]]
        elif config==4:
            # g4->g1: ? (assume same from g3->g4)
            core_sts=[None, 1,0,0, 0,1,1, 1,1,0]
            core_or=1
            mcells=[[(10,1),(11,1),(12,1),None,None],[(14,2),None,None,None,(13,1)],[(16,2),None,None,None,(15,1)],[(18,2),None,None,None,(17,1)],[(19,1),(20,1),(21,1),(22,1),None]]
        else:
            print(cfg)
            raise("invalid starting configuration")
        # membrane cells
        membrane={}
        for my in range(len(mcells)):
            for mx in range(len(mcells[my])):
                if mcells[my][mx]:
                    mi,mo = mcells[my][mx]
                    membrane[mi] = [mx-2,2-my,mo]
        return (core_sts, core_or, membrane)









#
