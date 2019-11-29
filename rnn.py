
import numpy as np

class RNN:
    def __init__(self\
        , input_dims=3, hidden_dims=5, output_dims=2\
        , learning_rate=0.5):
        # learning rate
        self.learning_rate = learning_rate
        # dimensions (hidden, output)
        self.input_dims = input_dims
        self.hidden_dims = hidden_dims
        self.output_dims = output_dims
        # init matrices (input, hidden, output) # M: F x C
        self.V = np.random.randn(self.hidden_dims, self.input_dims)
        self.U = np.random.randn(self.hidden_dims, self.hidden_dims)
        self.W = np.random.randn(self.output_dims, self.hidden_dims)
        # to accumulate weights (input, hidden, output)
        self.delta_V = np.zeros((self.hidden_dims, self.input_dims))
        self.delta_U = np.zeros((self.hidden_dims, self.hidden_dims))
        self.delta_W = np.zeros((self.output_dims, self.hidden_dims))
        # states (s0 is for looking back at t=1)
        s0 = np.array([np.zeros(self.hidden_dims)])
        self.states = [s0.T]
        self.outputs = []

    # for later
    def apply_deltas(self):
        # update
        self.V += self.learning_rate * self.delta_V
        self.U += self.learning_rate * self.delta_U
        self.W += self.learning_rate * self.delta_W
        # reset
        self.delta_V.fill(0.0)
        self.delta_U.fill(0.0)
        self.delta_W.fill(0.0)

    def sigmoid(self, z):
        return np.array([1/(1+np.exp(-i)) for i in z])

    def decide(self, x_in):
        # given an input x, decide next action
        # current input: input matrix · input vector .T
        x = np.array([np.array(x_in)])
        vx = np.dot(self.V, x.T)
        # past hidden state: hidden matrix · past hidden vector
        us = np.dot(self.U, self.states[-1])
        # net_in(t) = current input + past hidden state
        net_in = np.add(vx, us)
        # s(t) = f(net_in(t))
        s = self.sigmoid(net_in)
        # save to collection of states
        self.states.append(s)
        # convert hidden data into output matrix
        net_out = np.dot(self.W, s)
        # y(t) = g(net_out(t))???
        y = self.sigmoid(net_out)
        # save
        self.outputs.append(y)
        # convert NaN to zero and return just values
        y = [np.array([0.]) if np.isnan(i)==True else i[0] for i in y]
        # import pdb; pdb.set_trace()
        return y













        #
