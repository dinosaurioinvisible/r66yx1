
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


    def define_configs(self):
        # A config
        ca = np.array([ [2,0,0,0,2],
                        [2,0,1,0,0],
                        [0,0,0,1,0],
                        [0,1,1,1,0],
                        [0,0,0,0,0]])
        # B config
        cb = np.array([ [0,0,0,0,0],
                        [0,1,0,1,0],
                        [0,0,1,1,0],
                        [2,0,1,0,0],
                        [2,0,0,0,2]])
        # rotate and flip
        aconfigs = []; bconfigs = []
        for i in range(4):
            cxa = np.rot90(ca,i)
            cxb = np.rot90(cb,i)
            aconfigs.extend([cxa,np.flip(cxa,1)])
            bconfigs.extend([cxb,np.flip(cxb,1)])























#
