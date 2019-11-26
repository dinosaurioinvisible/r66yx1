
import numpy as np

class RNN:
    def __init__(self, x\
        , hidden_dims=3, output_dims=2\
        , learning_rate=0.5):
        # input
        # one more [] to make the vector transposable
        self.input_dims = len(x)
        self.x = np.array([x])
        # learning rate
        self.learning_rate = learning_rate
        # dimensions (hidden, output)
        self.hidden_dims = hidden_dims
        self.output_dims = output_dims
        # init matrices (input, hidden, output)
        # M: F x C
        self.V = np.random.randn(self.hidden_dims, self.input_dims)
        self.U = np.random.randn(self.hidden_dims, self.hidden_dims)
        self.W = np.random.randn(self.output_dims, self.hidden_dims)
        # to accumulate weights (input, hidden, output)
        self.delta_V = np.zeros((self.hidden_dims, self.input_dims))
        self.delta_U = np.zeros((self.hidden_dims, self.hidden_dims))
        self.delta_W = np.zeros((self.output_dims, self.hidden_dims))
        # states (s0 is for looking back at t=1)
        s0 = np.zeros((len(self.x), self.hidden_dims))
        self.states = [s0]
        self.decide()

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
        return np.array([1/1+np.exp(-i) for i in z])

    def softmax(self, z):
        normalizer = sum([np.exp(i) for i in z])
        return np.array([np.exp(i)/normalizer for i in z])

    def decide(self):
        # given an input x, decide next action
        # current input: input matrix · input vector .T
        xt = np.dot(self.V, self.x.T)
        # past hidden state: hidden matrix · past hidden vector
        past_s = np.dot(self.U, self.states[-1].T)
        # net_in(t) = current input + past hidden state
        net_in = np.add(xt, past_s)
        # s(t) = f(net_in(t))
        st = self.sigmoid(net_in)
        # save to collection of states (de-transpose)
        self.states.append(st.T)
        # convert hidden data into output matrix
        net_out = np.dot(self.W, st)
        # y(t) = g(net_out(t))
        y = self.softmax(net_out)
        return y

xin = np.random.rand(2)
RNN(xin)












        #
