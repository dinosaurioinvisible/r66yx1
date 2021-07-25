

    # ax22: env/membrane
    n_env = sum([len(ei) for mi,ei in glx.memb_rxs.items()])
    ax22.title.set_text("env ({}) -> memb ({})".format(n_env,len(glx.memb_rxs)))
    ax22.set_xlim([-10,266])
    ax22.set_ylim([-10,266])
    mxy = []
    for mx,envx in glx.memb_rxs.items():
        for envi in envx:
            rei = reduce(envi,bin_pos=24)
            rmx = reduce(mx,bin_pos=16)
            mxy.append([rmx,rei])
    mx,my = zip(*mxy)
    colors = np.random.rand(len(mxy))
    ax22.scatter(mx,my,c=colors,alpha=0.5)

    '''default trial: st41=NE, single glider, dashed wall world'''
    def single_dash(self,gtx,st0=41,dash=0,anim=False):
        # initialize world and glider
        x0,y0=int(self.wsize/2),int(self.wsize/2)
        self.set_world(st0,x0,y0,mode="single_dash",dash=dash)
        gl = Glider(gtx,st0,x0,y0)
        # run trial
        tlim=0
        for ti in range(self.tt):
            # get world domain
            gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
            # if all core elements are off, it dies
            if np.sum(gl.core)==0:
                if anim:
                    glx_anim(gl,self.world)
                return 0
            # if world object within glider domain (collision), it dies
            elif np.sum(gl_domain[1:6,1:6]):
                if anim:
                    glx_anim(gl,self.world)
                return 1
            # if gl doesn't move in time limit, it dies
            elif tlim > self.limit:
                if anim:
                    glx_anim(gl,self.world)
                return 2
            # stop before encounters bounding walls (just in case)
            elif min(gl.i,gl.j)<10 or max(gl.i,gl.j)>self.wsize-10:
                break
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim += 1
                if gl.ox > 0:
                    tlim=0
        # end and return
        gl.gl_loops()
        if anim:
            glx_anim(gl,self.world)
        return gl

    '''first step: survive different patterns'''
    def evolve_dashes(self):
        # generations
        for n_gen in range(self.gens):
            print("\n\ngeneration {}".format(n_gen))
            # env dashes
            for dash in range(1,128):
                # gts
                print("\n")
                self.glxs = []
                dead_by = [0,0,0,0]
                survived = defaultdict(int)
                # to avoid overpopulation
                self.mode = "dashes"
                if len(self.genotypes) > self.popsize:
                    self.mode = "full"
                    backup = deepcopy(self.genotypes[:int(self.popsize/10)])
                # trials
                for gi,gt in enumerate(self.genotypes):
                    # start with north dashes so dash values are (0:127)
                    gl = self.trial.dashes(gt,st0=41,dash=dash)
                    if type(gl)==int:
                        dead_by[gl] += 1
                    elif len(gl.txs)==0:
                        dead_by[3] += 1
                    else:
                        self.glxs.append(gl)
                        survived[(gl.cx_mode,gl.mx_mode)] += 1
                    print("gen={}, mode={}, dash={}/127, gl={}/{}, off={},cols={},tlim={},disc={} saved={} type={} {}".format(n_gen,self.mode,dash,gi+1,len(self.genotypes),dead_by[0],dead_by[1],dead_by[2],dead_by[3],len(self.glxs),survived,""*11),end='\r')
                # results, data check and optional visualization
                self.glxs = sorted(self.glxs,key=lambda x:len(x.txs),reverse=True)
                self.check_data(n_gen,dash)
                # in case full mode was too much
                if self.mode=="full" and len(self.glxs) < self.popsize/10:
                    print("\n\nbackup used, current genotypes={}".format(len(self.glxs)))
                    self.genotypes = backup
                else:
                    self.genotypes = []
                # reset and refill pop
                for gi,gl in enumerate(self.glxs):
                    for _ in range(self.offs):
                        gt = Genotype(glx=gl)
                        self.genotypes.append(gt)
                while len(self.genotypes) < self.popsize:
                    gt = Genotype()
                    self.genotypes.append(gt)
                # save (every 16 dashes)
                if dash%16==0:
                    self.glxs = self.glxs[:int(self.popsize/100)]
                    self.save_data(n_gen,dash)
            # generation end
            self.glxs = self.glxs[:int(self.popsize/100)]
            self.save_data(n_gen)


    # ax23
    if basic:
        # ax23: env/reaction
        ax23.title.set_text("env -> motion")
        # ax23.set_xlim([-0.5,4.5])
        ax23.set_ylim([-10,266])
        oxy = []
        for ox,envx in glx.env_rxs.items():
            for envi in envx:
                rei = reduce(envi,bin_pos=24)
                oxy.append([ox,rei])
        xo,xy = zip(*oxy)
        colors = np.random.rand(len(oxy))
        ax23.scatter(xo,xy,c=colors,alpha=0.5)

'''convert active membrane/wall pattern to int (clockwise)'''
def ext2int(ma):
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.flip(ma[-1,:]),np.flip(ma[:,0])]
    # if nothing
    if np.sum(ma_arrs)==0:
        return 0
    # linear array
    ma_ux = np.concatenate((ma_arrs[0][:-1],ma_arrs[1][:-1],ma_arrs[2][:-1],ma_arrs[3][:-1]))
    cn = len(ma_arrs[0])-1
    ei = ma_ux.argmax()
    wi = int(ei/cn)
    # one active vertex element (vals: 1 or 16/64 (first/last))
    if np.sum(ma_ux)==1 and ei%cn==0:
        # for simplicity just 1 (assuming some symmetry)
        return 1
    # 1 wall cases (1 central or more than 1 element)
    for wx in ma_arrs:
        if np.sum(wx)==np.sum(ma_ux):
            wx_int = arr2int(wx)
            return wx_int
    # 2 walls cases
    wl = ma_arrs[(wi+1)%4][:-1]
    wr = ma_arrs[(wi-1)%4][1:]
    wb = ma_arrs[(wi+2)%4][1:-1]
    if np.sum(wl)>0 and np.sum(wr)==np.sum(wb)==0:
        # wx = np.concatenate((wl,ma_arrs[wi]))
        wx
    elif np.sum(wr)>0 and np.sum(wl)==np.sum(wb)==0:
        # wx = np.concatenate((ma_arrs[wi],wr))
        wx
    elif np.sum(wb)>0 and np.sum(wl)==np.sum(wr)==0:
        wx
    # 3 or 4 walls?
    else:
        print("more than 2 walls?")
        import pdb; pdb.set_trace()
    wx_int = arr2int(wx)
    return wx_int

    else:
        # ax23: txs as trajectories
        ax23.title.set_text("gt: txs trajectories")
        for tk in glx.txs.keys():
            transients = glx.txs[tk]
            for transient in transients:
                x,y = 50,50
                xs = [x]
                ys = [y]
                om0 = transient[0][3]
                if om0==1:
                    x += 1
                elif om0==2:
                    y -= 1
                elif om0==3:
                    x -= 1
                elif om0==4:
                    y += 1
                xs.append(x)
                ys.append(y)
                for sti in transient[:-1]:
                    om = sti[5]
                    if om==1:
                        x += 1
                    elif om==2:
                        y -= 1
                    elif om==3:
                        x -= 1
                    elif om==4:
                        y += 1
                    xs.append(x)
                    ys.append(y)
            ax23.plot(xs,ys)

class Element:
    def __init__(self,gt,o0,s0):
        # genotype
        self.u = gt
        # self.x,self.y = x0,y0
        # 0=north, 1=east, 2=south, 3=west
        self.o = o0
        # signaling: 1/0
        self.sig = s0

    def update(self,env):
        # adjust env info according to current orientation
        ein = np.rot90(env,self.o).flatten()
        # convert to binary to map to output
        bi = int(''.join(str(int(i)) for i in ein),2)
        # search for response. If it isn't one, create it
        if not self.u[bi]:
            self.u[bi] = np.random.randint(0,8)
        # update
        self.sig,rm,lm = np.binary_repr(self.u[bi],3)
        # turn: rm=1 > right, lm=1 > left
        self.o = (self.o+rm-lm)%4
        # motion
        mx = 1 if (rm+lm)>1 else 0
        return mx

    # ax4: trial transitions (animated)
    ax4.set_xlim(0,525)
    ax4.set_ylim(0,525)
    # nodes
    txs = []
    for i,sti in enumerate(glx.hs):
        if i>0:
            tx = plt.Circle((glx.hs[i-1],glx.hs[i]),radius=5,color="orange",fill=True,visible=False)
            ax4.add_artist(tx)
            txs.append(tx)
    # looping nodes
    for i,cx in enumerate(glx.cycles):
        cx = cx+[cx[0]]
        if i>0:
            tx = plt.Circle((glx.hs[i-1],glx.hs[i]),radius=7,color="blue",fill=False,visible=True)
            ax4.add_artist(tx)
    # edges
    tx0, = ax4.plot([],[],color="grey",linestyle="dashed")
    tx1, = ax4.plot([],[],color="black",linestyle="dashed")

    '''bounded group motion'''
    def gl_motion(self,dxy):
        # dm = 0
        dx = dxy[1]-dxy[3]
        dy = dxy[0]-dxy[2]
        # select higher sum and move if higher than motion threshold
        if abs(dx)>abs(dy):
            # do = 1 if dx>0 else 3
            if abs(dx)>self.mt:
                self.j += int(dx/abs(dx))
                # dm = 1
        elif abs(dy)>abs(dx):
            # do = 0 if dy>0 else 2
            if abs(dy)>self.mt:
                self.i += int(-dy/abs(dy))
                # dm = 1
        # so if dx==dy (no dominant orientation)
        # else:
        #     do = -1
        # self.loc.append([self.i,self.j])
        # self.dodm.append([do,dm])

def gl_loops(self,r=2):
    for sti,[ci,mi] in enumerate(zip(self.core[:-r],self.memb[:-r])):
        loop = np.zeros((2,len(self.states))).astype(int)
        loop_seq = []
        wi = sti
        wx = sti+r
        # sliding window like
        while wx<len(self.states)-1:
            cx,mx = self.core[wx],self.memb[wx]
            if [ci,mi]==[cx,mx]:
                loop[0][wi:wx+1] = self.core[wi:wx+1]
                loop[1][wi:wx+1] = self.memb[wi:wx+1]
                # it could be the case that different seqs happen (pretty rare though)
                seq = [(c,m) for [c,m] in zip(self.core[wi:wx+1],self.memb[wi:wx+1])]
                if seq not in loop_seq:
                    loop_seq.append(seq)
                # windows skips to states after loop
                wi = wx+1
                wx = wi+r
            else:
                wx+=1
        # if something
        if len(loop_seq)>0:
            self.loops.append(loop)
            for seq in loop_seq:
                # from zero so it closes the loop (last->first)
                for si in range(0,len(seq)):
                    cs0,ms0 = seq[si-1]
                    cs,ms = seq[si]
                    if not [cs,ms] in self.cycles[(cs0,ms0)]:
                        self.cycles[(cs0,ms0)] += [[cs,ms]]

'''search for new loops (possible cycles)'''
def gl_loops(self):
    # look for loops in states
    for window_size in range(3,11):
        # sliding window
        for w0 in range(len(self.sts)-window_size):
            loop = False
            window_sts = self.sts[w0:w0+window_size]
            # check if loops
            if window_sts[0]==window_sts[-1]:
                # check that it isn't an iteration over the same loop
                iter = False
                for wi,window_st in enumerate(window_sts[1:-1]):
                    if window_st==window_sts[0]:
                        xloop = window_sts[:wi+1]
                        iloop = window_sts[wi+1:(wi+1)*2]
                        if xloop==iloop:
                            iter = True
                            break
                # check for loop cycles
                if not iter:
                    loop = window_sts[:-1]
                    loop_cycle = np.zeros(len(self.sts))
                    loop_cycle[w0:w0+window_size-1] = loop
                    # if it repeats during the remaining of the trial
                    n_loops = 1
                    for st0 in range(w0+window_size,len(self.sts)-window_size):
                        trial_window = self.sts[st0:st0+window_size-1]
                        if loop==trial_window:
                            loop_cycle[st0:st0+window_size-1] = loop
                            n_loops += 1
                    self.loops.append(loop_cycle)
                    # append to cycles if appears more than once
                    if n_loops>1 and loop not in self.cycles:
                        self.cycles.append(loop)

'''update according to re-oriented input'''
def xupdate(self,env):
    self.motion = [0]*4
    # core
    core_domain = np.zeros((7,7))+self.domain
    for ei,[i,j] in enumerate(self.ce_ij):
        # re-oriented surrounding space + recurrent state
        e_in = np.rot90(core_domain[i-1:i+2,j-1:j+2],self.eos[ei]).flatten()
        # search for response in gt
        bi = int(''.join(str(int(i)) for i in e_in),2)
        # create response if theres isn't one
        if not self.gt[bi]:
            self.gt[bi] = np.random.randint(0,8)
        esig,rm,lm = [int(ri) for ri in np.binary_repr(self.gt[bi],3)]
        # update element
        self.domain[i][j] = esig
        # 0,0:stay - 1,0:turn right, 0,1:turn left - 1,1:move forward
        self.eos[ei] = (self.eos[ei]+rm-lm)%4
        if rm+lm > 1:
            self.motion[self.eos[ei]] += 1
    # membrane
    mem_domain = np.zeros((7,7))+env
    mem_domain[2:5,2:5] = self.domain[2:5,2:5]
    for i,j in self.me_ij:
        # 0 if any activation around (not itself), 1 otherwise
        me_in = np.sum(mem_domain[i-1:i+2,j-1:j+2])-mem_domain[i][j]
        self.domain[i][j] = 0 if me_in > 0 else 1
    self.motion_fx()

'''update according to sum + state'''
    def update(self,gl_domain):
        self.motion = TODO
        new_domain = np.zeros((7,7))
        # core
        for ei,[i,j] in enumerate(self.ce_ij):
            # sum of surrounding signals
            esum = np.sum(gl_domain[i-1:i+2,j-1:j+2])-gl_domain[i][j]
            # state
            st = self.sts[ei]+gl_domain[i][j]
            self.sts[ei] = 0 if int(st)==1 else st
            # response index ((maxsum+1)*st)+sum: [0,17]
            ri = 9*int(st)+esum
            # response from map
            sig,rm,lm = self.gt[ei][ri]
            # update signal
            new_domain[i][j] = sig
            # update orientation and motion intention
        # membrane
        for ei,[i,j] in enumerate(self.me_ij):
            me_in = np.sum(gl_domain[i-1:i+2,j-1:j+2])
            if ei==0 or ei==4 or ei==11 or ei==15:
                th = 1
            elif ei==2 or ei==7 or ei==8 or ei==13:
                th = 3
            else:
                th =2
            new_domain[i][j] = 1 if me_in > th else 0

    def motion_fx(self,motion):
        # east/west
        mx = motion[1] - motion[3]
        # north/south
        my = motion[0] - motion[2]
        # dominant orientation
        #ox = np.sum(np.where(self.eos==1,1,0))-np.sum(np.where(self.eos==3,1,0))
        #oy = np.sum(np.where(self.eos==0,1,0))-np.sum(np.where(self.eos==2,1,0))
        #do = ox if abs(ox) > abs(oy) else oy
        # chose the higher and compare to threshold
        if max(abs(mx),abs(my)) > self.mt:
            if abs(mx) > abs(my):
                self.j += mx/abs(mx)
            else:
                self.i -= my/abs(my)
        self.hi.append(deepcopy(self.i))
        self.hj.append(deepcopy(self.j))

    def fin(self):
        # trial transitions
        self.txs.append(self.hs)
        # known cycles
        for cx in self.cycles:
            cy = False
            cycle = np.zeros(len(self.hs))
            for i in range(len(self.hs)-len(cx)):
                sti = self.hs[i:i+len(cx)]
                if cx==sti:
                    cy = True
                    cycle[i:i+len(cx)] = cx
            if cy:
                self.hcycles.append(cycle)
        # new cycles
        for wsize in range(2,11):
            # last window (wsize=3): 94,95,96 compared with 97,98,99
            for wi in range(len(self.hs)-wsize*2):
                # check if window states form a loop
                window_sts = self.hs[wi:wi+wsize]
                cy_sts = None
                cycle = np.zeros(len(self.hs))
                # compare sts to remaining trial sts
                for sti in range(wi+wsize,len(self.hs)-wsize):
                    cy = False
                    gl_sts = self.hs[sti:sti+wsize]
                    if window_sts==gl_sts:
                        cy = True
                        cycle[sti:sti+wsize] = gl_sts
                        cy_sts = window_sts
                if cy:
                    self.hcycles.append(cycle)
                    new = True
                    for known_cycle in self.cycles:
                        if cy_sts==known_cycle:
                            new = False
                    if new:
                        self.cycles.append(cy_sts)

'''group common vals in array'''
def arr2group(x,vals=4,xmax=False,bin=False):
    gi = []
    for vi in range(0,vals):
        gi.append(np.sum(np.where(x==vi,1,0)))
    if xmax:
        xmi = sorted([[xvi,xi] for xi,xvi in enumerate(gi)])[-1][1]
        if bin:
            xbi = [int(i) for i in np.binary_repr(xmi,2)]
            return xbi
        return xmi
    return gi

'''membrane signaling reaction'''
def membrane_fx(domain,me_ij=[],mx=None):
    mdomain=np.zeros((7,7))
    # reacts if any external cell is active
    if len(me_ij)>0:
        domain[1:6,1:6] = 0
        for [i,j] in me_ij:
            if np.sum(domain[i-1:i+2,j-1:j+2]) > 0:
                mdomain[i][j] = 1
        membrane = mdomain[1:6,1:6]
    # reacts if external input > internal input
    else:
        for j in range(1,6):
            mdomain[1][j] += np.sum(domain[0,j-1:j+2])-np.sum(domain[2,max(2,j-1):min(j+2,5)])
            mdomain[5][j] += np.sum(domain[6,j-1:j+2])-np.sum(domain[4,max(2,j-1):min(j+2,5)])
        for i in range(1,6):
            mdomain[i][1] += np.sum(domain[i-1:i+2,0])-np.sum(domain[max(2,i-1):min(i+2,5),2])
            mdomain[i][5] += np.sum(domain[i-1:i+2,6])-np.sum(domain[max(2,i-1):min(i+2,5),4])
        membrane = np.where(mdomain[1:6,1:6]>0,1,0)
    if not mx:
        return membrane
    # sum of all active external cells
    if mx=="all":
        msx = np.sum(membrane)
    # sum as 4 walls
    if mx==4:
        me = np.where(np.asarray([np.sum(membrane[0,:]),np.sum(membrane[:,4]),np.sum(membrane[4,:]),np.sum(membrane[:,0])])>0,1,0)
        msx = arr2int(me)
    # sum as corners + walls
    if mx==8:
        ml = np.sum(membrane[1:4,0])
        mr = np.sum(membrane[1:4,4])
        mu = np.sum(membrane[0,1:4])
        md = np.sum(membrane[4,1:4])
        mul = membrane[0][0]
        mur = membrane[0][4]
        mdl = membrane[4][0]
        mdr = membrane[4][4]
        me = np.where(np.asarray([mul,mu,mur,ml,mr,mdl,md,mdr])>0,1,0)
        msx = arr2int(me)
    # get encountered dash (only for 1 wall)
    if mx=="dash":
        d0 = domain[0,:]
        d1 = domain[:,6]
        d2 = domain[6,:]
        d3 = domain[:,0]
        dm = [d0,d1,d2,d3]
        di = np.asarray([np.sum(dx) for dx in dm]).argmax()
        msx = arr2int(dm[di])
    if not mx:
        raise Exception("mx argument unknown")
    return membrane,msx

'''convert the borders of some matrix to int'''
def ext2int(ma):
    ma_arrs = [ma[0,:],map[:,-1],ma[-1,:],ma[:,0]]
    ma_ints = [arr2int(mi) if np.sum(mi)>0 else 0 for mi in ma_arrs]
    base_len = len(ma_arrs[0])
    base = 2**base_len
    bi = 0
    # index number according to every combination (0,01,012,0123,...,2,23,3)
    for mi in ma_ints:
        mx = base*bi+mi if mi>0 else mx
        bi += 1
        for mj in ma_ints[i+1:base_len]:
            mx = base*bi+mj if mj>0 else mx
            bi += 1
            for mk in ma_ints[j+1:base_len]:
                mx = base*bi+mk if mk>0 else mx
                bi += 1
    return mx

#self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
# membrane, fixed o
self.eos[0:4] = 0
for mi in [4,9,14,19]:
    self.eos[mi] = 1
self.eos[21:] = 2
for mi in [5,10,15,20]:
    self.eos[mi] = 3

# membrane reacts-to-all (exterior) version
self.st = np.zeros((7,7))
gl_domain[2:5,2:5] = 0
for [i,j] in self.me_ij:
    if np.sum(gl_domain[i-1:i+2,j-1:j+2]) > 0:
        self.st[i][j] = 1
self.st = self.st[1:6,1:6]

#cxi = cx==sti
#if cxi.astype(np.ndarray).all():


# general response
# init
go = arr2group(self.eos,xmax=True,bin=True)
gr = [0]+go+[0]*4
gl_r0 = arr2int(np.asarray(gr))
self.grs.append(gl_r0)
# update
go = arr2group(self.eos,xmax=True,bin=True)
gl_response = arr2int(np.asarray(gxy+go+gms))
self.grs.append(gl_response)


# known cycles
for cx in self.cycles:
    cy = False
    cycle = np.zeros(len(self.hs))
    for i in range(len(self.hs)-len(cx)):
        sti = self.hs[i:i+len(cx)]
        if cx==sti:
            cy = True
            cycle[i:i+len(cx)] = cx
    if cy:
        cycles.append(cycle)


# cycles (no pos needed)
gx = nx.Graph()
for txi in self.txs:
    for i,tx in enumerate(txi):
        gx.add_node(tx)
        if i>0:
            gx.add_edge(txi[i-1],tx)
# self.cycles = list(nx.simple_cycles(gx))
self.cycles = nx.cycle_basis(gx)

'''initial cycles for the default glider'''
def set_cycles():
    # bsts = []
    # bgrs = []
    # btrs = []
    # btrs = defaultdict(list)
    btrs = {}
    a = np.array([0,0,1,1,0,1,0,1,1])
    b = np.array([1,0,0,0,1,1,1,1,0])
    # for each cycle
    for do in range(4):
        c1,c2 = arr2int(a,b,rot=do)
        c3,c4 = arr2int(a,b,rot=do,transp=True)
        # dict version
        btrs[(c1,0,0)] = [c2,0,0]     #[[c2,0],[c3,0],[c4,0],[c1,0]]
        btrs[(c2,0,0)] = [c3,0,0]     #[[c3,0],[c4,0],[c1,0],[c2,0]]
        btrs[(c3,0,0)] = [c4,0,0]     #[[c4,0],[c1,0],[c2,0],[c3,0]]
        btrs[(c4,0,0)] = [c1,0,0]     #[[c1,0],[c2,0],[c3,0],[c4,0]]
        # bsts.extend([c1,c2,c3,c4])
        # btrs.extend([[c1,c2],[c2,c3],[c3,c4],[c4,c1],[0,0,0,0]])
        # btrs.append([c1,c2,c3,c4])
        # o1r,o1l = [int(o) for o in np.binary_repr(((1-do)%4),2)]
        # o3r,o3l = [int(o) for o in np.binary_repr(((1+do+1)%4),2)]
        # r1,r2 = arr2int(np.asarray([1,o1r,o1l,0,0,0,0]),np.asarray([0,o1r,o1l,0,0,0,0]))
        # r3,r4 = arr2int(np.asarray([1,o3r,o3l,0,0,0,0]),np.asarray([0,o3r,o3l,0,0,0,0]))
        # bgrs.extend([r1,r2,r3,r4])
    return btrs

'''element's base responses (just 4 cycles)'''
def set_responses():
    # map: gl_in -> gl_response
    variations = False
    variations2 = False
    membrane_gt = False
    # gt = [None]*512
    gt = {}
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
    aevijc = [[[1,1],[3,1]],[[1,3],[3,3]],[[1,1],[1,3]],[[3,1],[3,3]]]
    aeviji = [[0,6],[2,8],[0,2],[6,8]]
    # cases where 2 membrane cells can be on
    mvij2 = [[0,1],[0,3],[1,0],[3,0]]
    aevij2 = [[1,1],[1,3],[1,1],[3,1]]
    aevij2i = [0,2,0,2]
    aevij2c = [[1,2],[1,2],[2,1],[2,1]]
    aevij2ci = [1,1,3,3]
    aevij2co = [0,0,3,3]
    # for every state of A
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
        if membrane_gt:
            for mi in range(0,8):
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

def set_combined_os():
    cos = []
    for o1 in range(0,10):
        for o2 in range(0,10):
            for o3 in range(0,10):
                for o4 in range(0,10):
                    so = o1+o2+o3+o4
                    xo = ''.join(str(o) for o in [o1,o2,o3,o4])
                    if so==9:
                        cos.append(xo)
    cos = (np.asarray(cos).astype(int)/9).astype(int)
    return cos

# arrows
if arrows:
    for edge in gx.edges():
        graph.add_annotation(
            x = gx.nodes[edge[1]]['pos'][0],
            y = gx.nodes[edge[1]]['pos'][1],
            ax = gx.nodes[edge[0]]['pos'][0],
            ay = gx.nodes[edge[0]]['pos'][1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,arrowsize=3,arrowwidth=1,arrowcolor="black")

# # plot graph
# graph = go.Figure(data=[edge_trace,node_trace],
#                 layout=go.Layout(
#                 title="genotype graph mapping, timesteps={}, recurrences={}".format(len(glx.txs),glx.recs),
#                 titlefont_size=16,
#                 showlegend=False,
#                 #hovermode='closest',
#                 margin=dict(b=20,l=10,r=10,t=30),
#                 xaxis=dict(showgrid=False,zeroline=False,showticklabels=True),
#                 yaxis=dict(showgrid=False,zeroline=False,showticklabels=True)))
# graph.show()


'''
# south-east
se1 = [[0,0,1],[1,0,1],[0,1,1]]
se2 = [[1,0,0],[0,1,1],[1,1,0]]
se3 = [[0,1,0],[0,0,1],[1,1,1]]
se4 = [[1,0,1],[0,1,1],[0,1,0]]
se = [se1,se2,se2,se4]

# south-west
sw1 = [[1,0,0],[1,0,1],[1,1,0]]
sw2 = [[0,0,1],[1,1,0],[0,1,1]]
sw3 = [[0,1,0],[1,0,0],[1,1,1]]
sw4 = [[1,0,1],[0,1,1],[0,1,0]]
sw = [sw1,sw2,sw3,sw4]

# north-east
ne1 = [[0,1,1],[1,0,1],[0,0,1]]
ne2 = [[1,1,0],[0,1,1],[1,0,0]]
ne3 = [[1,1,1],[0,0,1],[0,1,0]]
ne4 = [[0,1,0],[0,1,1],[1,0,1]]
ne = [ne1,ne2,ne3,ne4]

# north-west
nw1 = [[1,1,0],[1,0,1],[1,0,0]]
nw2 = [[0,1,1],[1,1,0],[0,0,1]]
nw3 = [[1,1,1],[1,0,0],[0,1,0]]
nw4 = [[0,1,0],[1,1,0],[1,0,1]]
nw = [nw1,nw2,nw3,nw4]
'''

###
