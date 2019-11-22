
import numpy as np

# do I really need a matrix for inputs??

class RNN:
    def __init__(self, input\
            , hidden_dims=3, output_dims=2\
            , learning_rate=0.5):
        # input
        self.x = input
        # dimensions
        self.input_dims = len(self.x)
        self.hidden_dims = hidden_dims
        self.output_dims = output_dims
        # parameters
        self.learning_rate = learning_rate
        # input
        self.V = np.random.randn(self.hidden_dims, self.input_dims)
        # hidden
        self.U = np.random.randn(self.hidden_dims, self.input_dims)
        # output
        self.W = np.random.randn(self.output_dims, self.input_dims)
        # to accumulate weight updates
        self.delta_V = np.zeros((self.hidden_dims, self.input_dims))
        self.delta_U = np.zeros((self.hidden_dims, self.hidden_dims))
        self.delta_W = np.zeros((self.output_dims, self.hidden_dims))

    def apply_deltas(self):
        # update
        self.V += self.learning_rate*self.delta_V
        self.U += self.learning_rate*self.delta_U
        self.W += self.learning_rate*self.delta_W
        # reset
        self.delta_V.fill(0.0)
        self.delta_U.fill(0.0)
        self.delta_W.fill(0.0)

    def sigmoid(self, z):
        return [1/(1+np.exp(-i)) for i in z]

    def softmax(self, z):
        normalizer = sum([np.exp(i) for i in z])
        return [np.exp(i)/normalizer for i in z]

    def decide(self):
        # given an input x, decide
        # s has one more row to look back to t=0
        s = np.zeros((self.input_dims+1, self.hidden_dims))
        y = np.zeros((self.input_dims, self.output_dims))
        # generate behaviour for t timesteps
        import pdb; pdb.set_trace()
        for t in range(self.input_dims):
            # net_in(t) = sum(U.s(t-1) + V.x(t))
            net_in = np.dot(self.V, self.x[t].T) + np.dot(self.U, s[t-1].T)
            # s(t) = f(net_in(t))
            s[t] = self.sigmoid(net_in)
            # net_out = W*s(t)
            net_out = np.dot(self.W, s[t].T)
            # y(t) = g(net_out(t))
            y[t] = self.softmax(net_out)
        print(y)
        print(s)
        return y,s


x_in = np.random.randn(2)
ex = RNN(x_in)
ex.decide()















#
