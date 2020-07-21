
import numpy  as np

class RNN:
    def __init__(self, genotype):
        # dimensions
        self.n_input = genotype.n_input
        self.n_hidden = genotype.n_hidden
        self.n_output = genotype.n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        # excitatory and inhibitory/veto connectivity matrices
        self.W = genotype.W
        self.V = genotype.V
        # number of units for inputs
        self.e_in = genotype.e_in
        self.vs_n = genotype.vs_n
        self.olf_n = genotype.olf_n
        self.com_len = genotype.com_len
        # threshold and noise values
        self.ut = genotype.ut
        self.lt = genotype.lt
        self.vt = genotype.vt
        self.noise = genotype.noise
        # internal states (empty state for t=0)
        self.e_states = [np.zeros((self.n_net,1))]
        self.h_states = [np.zeros((self.n_net,1))]


    def update(self, x):
        # internal activation for next step
        e_state = np.zeros((self.n_net,1))
        h_state = np.zeros((self.n_net,1))

        # sensory inputs (x)
        x = np.array([x]).T
        # excitatory input: sensory input + previous recurrent states
        ex = x + self.e_states[-1][:self.n_input]
        # inhibitory input: only previous recurrent states
        hx = self.h_states[-1][:self.n_input]
        # instead of the common case input-> hidden -> output, here f(x) is applied for every unit
        xe, xh = self.neuron_fx(ex,hx)
        # propagation according to the connectivity matrices W (excitatory) and V (veto/inhibitory)
        # NOTE: as is potentially fully connected, W and V shapes are (n_net, n_net)
        # in this case: W.shape = (n_net, n_input); xe.shape = (n_input, 1) -> wx.shape = (n_net, 1)
        wx = np.dot(self.W[0:self.n_net,0:self.n_input], xe)
        vx = np.dot(self.V[0:self.n_net,0:self.n_input], xh)
        # save backward/self propagation for next step (only towards the input layer in this case)
        retro_wx = wx[:self.n_input].copy()
        retro_wx.resize((self.n_net,1))
        e_state += retro_wx
        retro_vx = vx[:self.n_input].copy()
        retro_vx.resize((self.n_net,1))
        h_state += retro_vx

        # hidden layer (u)
        eu = wx[self.n_input:self.n_input+self.n_hidden] + self.e_states[-1][self.n_input:self.n_input+self.n_hidden]
        hu = self.h_states[-1][self.n_input:self.n_input+self.n_hidden]
        # go through hidden layer nodes
        ue, uh = self.neuron_fx(eu,hu)
        # propagation W.shape = (n_net, n_hidden), ue.shape (n_hidden, 1)
        wu = np.dot(self.W[0:self.n_net,self.n_input:self.n_input+self.n_hidden], ue)
        vu = np.dot(self.V[0:self.n_net,self.n_input:self.n_input+self.n_hidden], uh)
        # add backwards/self activation propagation for next step
        retro_wu = wu[:self.n_input+self.n_hidden].copy()
        retro_wu.resize((self.n_net,1))
        e_state += retro_wu
        retro_vu = vu[:self.n_input+self.n_hidden].copy()
        retro_vu.resize((self.n_net,1))
        h_state += retro_vu

        # output layer (o)
        eo = wx[self.n_input+self.n_hidden:] + wu[self.n_input+self.n_hidden:] + self.e_states[-1][self.n_input+self.n_hidden:]
        ho = vx[self.n_input+self.n_hidden:] + vu[self.n_input+self.n_hidden:] + self.h_states[-1][self.n_input+self.n_hidden:]
        # go through nodes
        oe, oh = self.neuron_fx(eo,ho)
        # propagation (all for next step in this case) shape = (n_net, 1)
        wo = np.dot(self.W[0:self.n_net,self.n_input+self.n_hidden:], oe)
        vo = np.dot(self.V[0:self.n_net,self.n_input+self.n_hidden:], oh)
        # add activation and save
        e_state += wo
        h_state += vo
        self.e_states.append(e_state)
        self.h_states.append(h_state)
        # motor output
        m1 = oe[0]-oe[1]
        m2 = oe[2]-oe[3]
        # attentional outputs
        olf_i = 4 + self.olf_n
        olf_attn = oe[4:4+olf_i] #if olf_i <= len(self.n_output) else np.array([])
        vs_i = olf_i + self.vs_n
        vs_attn = oe[olf_i:vs_i] #if vs_i <= len(self.n_output) else np.array([])
        # communication
        com_i = vs_i + self.com_len
        com = oe[vs_i:com_i] #if com_i <= len(self.n_output) else np.array([])
        # whole output (y)
        return m1, m2, olf_attn, vs_attn, com

    def neuron_fx(self, x, h):
        # veto output (from excitatory inputs)
        inh = np.where(x>=self.vt, 1, 0)
        # veto input (from inhibitory inputs)
        v = np.where(h>0, 0, 1)
        # random noise
        noise = np.array([np.random.uniform(-self.noise,self.noise,len(x))]).T
        x += noise
        # transfer function
        x = np.where(x>=self.ut,1,x)
        x = np.where(x<=self.lt,0,x)
        x = np.where((x>self.lt) & (x<self.ut), (x-self.lt)/(self.ut-self.lt), x)
        # V(x)*T(x)
        exc = x*v
        return exc, inh











#
