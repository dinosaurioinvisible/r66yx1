

lx = []
for i in range(16):
    lx.append([np.binary_repr(i),i])
pwi_states = np.zeros(16)
for li in lx:
    px = True
    for pi in pw_indexes:
        if int(li[0][pi]) != sti[pi]:
            px = False
    if px==True:
        pwi_states[li[1]] += 1

'''
IIT repertoires
'''
def repertoires_fx(gt):
    cxrep = {}
    exrep = {}



'''
integrated information
a) sum of the inf of parts vs inf of the system
b) minimal partition
'''
def ii_fx(sts_data,vxdist,cxrep,exrep,uxrep):
    # synergistic, intrinsic, integrated
    info = {}
    info['syn'] = {}
    info['int'] = {}
    info['phi'] = {}
    # mechanisms
    mx_sts = [(sta,stb,stc),(sta,stb,std),(sta,stc,std),(stb,stc,std),(sta,stb,stc,std)]
    mx_names = ['a','b','c','d','abcd']
    # distance matrix
    dmx3 = dist_matrix(dim=8,cost=0.5)
    dmx4 = dist_matrix(dim=16,cost=0.5)
    # syn_info, int_info, ii_info = [],[],[]
    for ti in range(1,len(sts_data)-1):
        # state of every element cell
        sta,stb,stc,std = int2arr(sts_data[i],arr_len=4)
        # prediction of next system st from current mechanism sts
        a_info = vxdist['a'][sta,stb,stc][sts_data[i+1]]
        b_info = vxdist['b'][sta,stb,std][sts_data[i+1]]
        c_info = vxdist['c'][sta,stc,std][sts_data[i+1]]
        d_info = vxdist['d'][stb,stc,std][sts_data[i+1]]
        # prediction of the system with respect to itself
        v_info = vxdist['abcd'][sta,stb,stc,std][sts_data[i+1]]
        # compare
        dx_info = v_info - sum([a_info,b_info,c_info,d_info])
        # syn_info.append([a_info,b_info,c_info,d_info,v_info,dx_info])
        info['syn'][]
        # b)
        mx_cei = []
        for mx,mx_st in zip(mx_names,mx_sts):
            # intrinsic information for every mechanism
            # cause info: dist(cause rep | uc past rep (uniform))
            cx = cxrep[mx][mx_st][sts_data[i-1]]
            uxp = np.array([1/len(mx_st)]*len(mx_st))
            dmx = dmx3 if len(mx_st)==3 else dmx4
            ci = emd(cx,uxp,dmx)
            info['crep'][mx][ti] = cx
            info['ci'][mx][ti] = ci
            # effect information: dist(effect rep | uc fut rep)
            ex = exrep[mx][mx_st][sts_data[i+1]]
            uxf = uxrep[mx][mx_st]
            ei = emd(cx,uxf,dmx)
            info['erep'][mx][ti] = ex
            info['ei'][mx][ti] = ei
            # cause effect information
            cei = min(ci,ei)
            info['cei'][mx][ti] = cei
            mx_cei.append(cei)
            # integrated information
            cmip = min(mx_cei)


        system_ii = info['cei']['abcd'][ti]


        a_ci = cxrep['a'][sta,stb,stc][sts_data[i-1]]
        b_ci = cxrep['b'][sta,stb,std][sts_data[i-1]]
        c_ci = cxrep['c'][sta,stc,std][sts_data[i-1]]
        d_ci = cxrep['d'][stb,stc,std][sts_data[i-1]]
        v_ci = cxrep['abcd'][sta,stb,stc,std][sts_data[i-1]]
        ci = [a_ci,b_ci,c_ci,d_ci,v_ci]
        # effect information for every mechanism
        a_ei = exrep['a'][sta,stb,stc][sts_data[i+1]]
        b_ei = exrep['b'][sta,stb,std][sts_data[i+1]]
        c_ei = exrep['c'][sta,stc,std][sts_data[i+1]]
        d_ei = exrep['d'][stb,stc,std][sts_data[i+1]]
        v_ei = exrep['abcd'][sta,stb,stc,std][sts_data[i+1]]
        ei = [a_ei,b_ei,c_ei,d_ei,v_ei]
        # intrinsic information
        a_int = min(a_ci,a_ei)
        b_int = min(b_ci,b_ei)
        c_int = min(c_ci,c_ei)
        d_int = min(d_ci,d_ei)
        v_int = min(v_ci,v_ei)
        intrinsic = [a_int,b_int,c_int,d_int,v_int]
        mip = min(intrinsic)
        #
        # save data
        for ni,xi in enumerate(['a','b','c','d','abcd']):
            info['ci'][xi][ti] = ci[ni]
            info['ei'][xi][ti] = ei[ni]
            info['intrinsic'][xi][ti] = min(ci[ni],ei[ni])


        # minimal partition


        # save data
        for ni,xi in zip(['a','b','c','d','abcd'],[a_ci,b_ci,c_ci,d_ci,v_ci]):
            info['ci'][ni][ti][xi]



'''
cause repertoire:
causal probability distribution
for every mechanism (mx) in state (sti)
distribution (cr) of the possible past states (stp)
'''
def get_repertoires(gt):
    # repertoires are dicts for access and plots
    cause_reps = {}
    effect_reps = {}
    uce_reps = {}
    # more than 3 elements mechanisms
    emx_names = ['a','b','c','d','ab','ac','bd','cd','abc','abd','acd','bcd','abcd']
    mx3_indexes = [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
    emx_indexes = [[0],[1],[2],[3],[0,1],[0,2],[1,3],[2,3],[0,1,2],[0,1,3],[0,2,3],[1,2,3],[0,1,2,3]]
    # define repertoires
    for name in emx_names:
        cause_reps[name] = {}
        effect_reps[name] = {}
        # for 3 elements mechanisms
        if len(name) == 1:
            for stc in [0,1]:
                cause_reps[name][stc] = np.zeros(8).astype(int)
                effect_reps[name][stc] = np.zeros(8).astype(int)
        else:
            for bi in range(2**len(name)):
                bsts = int2arr(bi,arr_len=len(name))
                cause_reps[name][tuple(bsts)] = np.zeros(16).astype(int)
                effect_reps[name][tuple(bsts)] = np.zeros(16).astype(int)
        # for unconstrained reps
        if len(name) == 1:
            uce_reps[name] = np.zeros(8).astype(int)
    uce_reps['abcd'] = np.zeros(16).astype(int)
    # full domain (including agent cells)
    domain_range = 2**21
    for domain in tqdm(range(domain_range)):
        # elements states
        dx = int2arr(domain,arr_len=21)
        stp_a = dx[5]
        stp_b = dx[9]
        stp_c = dx[11]
        stp_d = dx[15]
        # if dx[10] == 1:
        # system state (which is the frame mechanism for all)
        mx_sti = [stp_a,stp_b,stp_c,stp_d]
        a_in = arr2int(np.asarray([dx[0],dx[1],dx[2],dx[4],dx[5],dx[6],dx[9],dx[10],dx[11]]))
        b_in = arr2int(np.asarray([dx[3],dx[4],dx[5],dx[8],dx[9],dx[10],dx[13],dx[14],dx[15]]))
        c_in = arr2int(np.asarray([dx[5],dx[6],dx[7],dx[10],dx[11],dx[12],dx[15],dx[16],dx[17]]))
        d_in = arr2int(np.asarray([dx[9],dx[10],dx[11],dx[14],dx[15],dx[16],dx[18],dx[19],dx[20]]))
        sta = gt[0][a_in]
        stb = gt[1][b_in]
        stc = gt[2][c_in]
        std = gt[3][d_in]
        mx_stx = [sta,stb,stc,std]
        for mx_name,indexes in zip(emx_names,emx_indexes):
            # for mechanisms of 3 elements
            if len(indexes) == 1:
                mx_sti_index = arr2int(np.asarray([mx_sti[ei] for ei in mx3_indexes[indexes[0]]]))
                mx_stx_index = arr2int(np.asarray([mx_stx[ei] for ei in mx3_indexes[indexes[0]]]))
                exs_stx = mx_stx[indexes[0]]
                exs_sti = mx_sti[indexes[0]]
            else:
                mx_sti_index = arr2int(np.asarray(mx_sti))
                mx_stx_index = arr2int(np.asarray(mx_stx))
                exs_stx = tuple([mx_stx[i] for i in indexes])
                exs_sti = tuple([mx_sti[i] for i in indexes])
            # cause repertoires: elements (t) -> mechanism (t-1)
            # counts: element st (t+1) -> mechanism st (t)
            cause_reps[mx_name][exs_stx][mx_sti_index] += 1
            # effect repertoires: elements (t) -> mechanism (t+1)
            # counts: elements (t) -> mechanism (t+1)
            effect_reps[mx_name][exs_sti][mx_stx_index] += 1
            # unconstrained future repertoire
            # counts all future states independently of its inputs (current sts)
            try:
                uce_reps[mx_name][mx_stx_index] += 1
            except:
                uce_reps['abcd'][mx_stx_index] += 1
    # convert counts to distributions
    for name in emx_names:
        for key,count in cause_reps[name].items():
            cause_reps[name][key] = count/np.sum(count)
        for key,count in effect_reps[name].items():
            effect_reps[name][key] = count/np.sum(count)
    for name,count in uce_reps.items():
        uce_reps[name] = count/np.sum(count)
    return cause_reps, effect_reps, uce_reps

        # wcopy = world.astype(int)
        # for wi in range(world_size):
        #     for wj in range(world_size):
        #         wij = wcopy[wi,wj]
        #         nb = np.sum(wcopy[max(wi-1,0):wi+2,max(wj-1,0):wj+2]) - wij
        #         world[wi,wj] = 1 if nb==3 or (wij==1 and nb==2) else 0



def unit_gt(n_cells=4):
    # for every state
    st_range = 2**n_cells
    # for every environmental circumstance
    env_range = 2**(4+n_cells)
    # there should be a transition to another state
    genotype = np.random.randint(0,st_range,size=(st_range,env_range))
    return genotype

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# visualization of state transitions
# same initial state, different environmental conditions
def unit_st_transitions(gt,sti=6):
    gx = nx.DiGraph()
    # transitions from certain state i to different states x
    gx.add_nodes_from(range(len(gt)))
    # count sti->stx transitions
    tx_recurrence = defaultdict(int)
    for stx in gt[sti]:
        tx_recurrence[stx] += 1
    # add edges with recurrence weights
    for stx in gt[sti]:
        gx.add_edge(sti,stx,weight=tx_recurrence[stx])
    # plot
    x,weights = zip(*nx.get_edge_attributes(gx,'weight').items())
    cbar = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0,vmax=max(weights)))
    plt.colorbar(cbar)
    nx.draw_circular(gx,edge_color=weights,with_labels=True)
    plt.show()

# visualization of state transitions
# different initial state, same environmental conditions
def unit_env_transitions(gt,env=0):
    gx = nx.DiGraph()
    # transitions from every state i to different states x
    gx.add_nodes_from(range(len(gt)))
    for txi,txs in enumerate(gt):
        gx.add_edge(txi,txs[env])
    # plot
    nx.draw_circular(gx,with_labels=True)
    plt.show()

'''Ring unit, unique genotype'''
class RingUnit:
    def __init__(self,gt,n_cells,i,j,st0):
        # elements and gt
        self.gt = gt
        self.n_cells = n_cells
        # location
        self.i, self.j = i,j
        self.cell_locs = ring_locs(i,j,r=int(self.ncells/4))
        self.env_locs = ring_locs(i,j,r=int(1+self.ncells/4))
        # state
        self.st = st0
        self.cell_sts = int2arr(st0,arr_len=ncells)
        #self.st_hist = [st0]

    def update(self,world):
        # read environment
        env = []
        for [ci,cj] in self.env_locs:
            env.append(world[ci,cj])
        env_in = arr2int(np.asarray(env))
        # transition to new state
        self.st = self.gt[env_in]
        # individual states
        self.cell_sts = int2arr(self.st,arr_len=self.ncells)
        # save
        #self.st_hist.append(self.st)



'''trial for the ring unit'''
def unit_trial(gt,st0=6,n_trials=10,time=1000,world_size=10,rain_threshold=1):
    # set empty world
    world = np.zeros((world_size,world_size)).astype(int)
    # init and allocate ring agent in the center
    xy = int(world_size/2)
    agent = RingUnit(gt=gt,n_cells=4,i=xy,j=xy,st0=st0)
    # begin trials
    # v1: drops only fall from top to bottom
    # v1: drops dissapear after contact with agent
    end_times = []
    for tx in range(n_trials):
        ti = 0
        while ti < time:
            # update world
            rain = np.random.normal(0,rain_sd,world_size)
            rain = np.where(rain>1,1,0)
            world = np.vstack(rain,world[:-1])
            # update agent
            agent.update(world)
            for [ci,cj],cst in zip(agent.cell_locs,agent.cell_sts):
                world[ci,cj] = cst
            # update core
            nb = np.sum(agent.i-1:agent.i+2,agent.j-1:agent.j+2) - 1
            if nb < 2 or nb > 3:
                break
            ti += 1
        end_times.append(ti)
    return end_times


#
