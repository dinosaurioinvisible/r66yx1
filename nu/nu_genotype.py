
import numpy as np

class Genotype:
    def __init__(self,map=None,flex=0):
        self.flex = flex
        self.map = map
        if self.map == None:
            self.map = self.new_map()

    def new_map(self):
        # map: gl_in -> gl_response
        variations = True
        variations2 = False
        gt = [None]*512
        a1 = np.array([0,0,1,1,0,1,0,1,1])
        a2 = np.array([1,0,0,0,1,1,1,1,0])
        a3 = np.array([0,1,0,0,0,1,1,1,1])
        a4 = np.array([1,0,1,0,1,1,0,1,0])
        at = [a1,a2,a3,a4,a1]
        # these have cycles of orientations
        aeo13579 = [1,1,2,2]
        aei13579 = [0,2,4,6,8]
        aer13579 = [[1,1],[1,0],[1,1],[0,1]]
        # these have fixed orientations
        aeo2468 = [0,3,1,2]
        aei2468 = [1,3,5,7]
        # membrane cell that can be on
        mvij = [[[0,0],[4,0]],[[0,4],[4,4]],[[0,0],[0,4]],[[4,0],[4,4]]]
        aevijc = [[[1,1],[3,1]],[[1,3],[3,3]],[[1,1],[3,3]],[[3,1],[3,3]]]
        aeviji = [[0,6],[2,8],[0,2],[6,8]]
        mvij2 = [[0,1],[0,3],[1,0],[3,0]]
        aevij2 = [[1,1],[1,3],[1,1],[3,1]]
        aevij2i = [0,2,0,2]
        aevij2c = [[1,2],[1,2],[2,1],[2,1]]
        aevij2ci = [1,1,3,3]
        aevij2co = [0,0,3,3]
        # for very state of A
        for ai in range(len(at)-1):
            xa = np.zeros((5,5))
            xa[1:4,1:4] = at[ai].reshape(3,3)
            eo = aeo13579[ai]
            # diagonals (x)
            for ei,[i,j] in zip(aei13579,[[1,1],[1,3],[2,2],[3,1],[3,3]]):
                ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
                eb = int(''.join(str(int(i)) for i in ev),2)
                rm,lm = aer13579[ai]
                gt[eb] = [at[ai+1][ei],rm,lm]
            # cross (+)
            for ei,eoc,[i,j] in zip(aei2468,aeo2468,[[1,2],[2,1],[2,3],[3,2]]):
                ev = np.rot90(xa[i-1:i+2,j-1:j+2],eoc).flatten()
                eb = int(''.join(str(int(i)) for i in ev),2)
                em = 0 if at[ai][ei] == 1 else 1
                gt[eb] = [at[ai+1][ei],em,em]
            # membrane
            for mi in range(1,8):
                gt[mi] = [0,0,0]
            # known viable membrane variations
            if variations:
                for [vi,vj] in mvij[ai]:
                    xa[vi][vj] = 1
                for ei,[i,j] in zip(aeviji[ai],aevijc[ai]):
                    ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
                    eb = int(''.join(str(int(i)) for i in ev),2)
                    rm,lm = aer13579[ai]
                    gt[eb] = [at[ai+1][ei],rm,lm]
            if variations2:
                for [vi,vj] in mvij2[ai]:
                    xa[vi][vj] = 1
                for ei,[i,j] in zip(aevij2i,aevij2):
                    ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
                    eb = int(''.join(str(int(i)) for i in ev),2)
                    rm,lm = aer13579[ai]
                    gt[eb] = [at[ai+1][ei],rm,lm]
                for ei,eoc,[i,j] in zip(aevij2ci,aevij2co,aevij2c):
                    ev = np.rot90(xa[i-1:i+2,j-1:j+2],eoc).flatten()
                    eb = int(''.join(str(int(i)) for i in ev),2)
                    em = 0 if at[ai][ei] == 1 else 1
                    gt[eb] = [at[ai+1][ei],em,em]
        return gt

Genotype()
