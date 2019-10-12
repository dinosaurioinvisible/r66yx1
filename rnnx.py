
# coding: utf-8
from rnnmath import *
import numpy as np
from sys import stdout
import time
import math
from tqdm import tqdm

class RNNx(object):

    def __init__(self, p_size, hidden_dims):

        # initialize with random weight matrices
        self.p_size = p_size
        self.hidden_dims = hidden_dims

        # hidden -> hidden
        self.U = np.random.randn(self.hidden_dims, self.hidden_dims)*np.sqrt(0.1)
        # input -> hidden
        self.V = np.random.randn(self.hidden_dims, self.p_size)*np.sqrt(0.1)
        # hidden -> output
        self.W = np.random.randn(self.p_size, self.hidden_dims)*np.sqrt(0.1)

        # weights updates
        self.deltaU = np.zeros((self.hidden_dims, self.hidden_dims))
        self.deltaV = np.zeros((self.hidden_dims, self.p_size))
        self.deltaW = np.zeros((self.p_size, self.hidden_dims))

    def apply_deltas(self, learning_rate):
        # update
        self.U += learning_rate*self.deltaU
        self.V += learning_rate*self.deltaV
        self.W += learning_rate*self.deltaW
        # reset matrices
        self.deltaU.fill(0.0)
        self.deltaV.fill(0.0)
        self.deltaW.fill(0.0)

    # sigmoid
    def sigmoid(z):
        return [1/1+math.exp(-i) for i in z]
    # softmax
    def softmax(z):
        normalizer = sum([math.exp(i) for i in z])
        return [math.exp(i)/normalizer for i in z]

    # perturbation to "perception"
    def percept(self, perturbation):
        perception = np.zeros(self.p_size)
        '''
        here is important to define what kind of input
        or how the inputs will be perceived
        1-hot vectors work ok for dictionary entries, but
        for perturbations from the environment
        this function should be dynamic!
        from a whole matrix for example
        to get a random perception
        as one of the genetic features
        so that through time, perception of the world can change
        so the whole spectrum of possible perturbations
        should be codified in a matrix(?)
        and from this matrix
        just a portion, a vector(?), is internalized
        according to the particular function
        random at first, but genetecly passed from then on
        '''
        # perception
        return perception

    def act(self, x):
        # given input x:
        # s-matrix = hidden states, y-matrix = output_states
        s = np.zeros((len(x)+1, self.hidden_dims))
        y = np.zeros((len(x), self.x_size))
        # 
        for t in range(len(x)):
            # x to percibited x
            xt = self.percept(x[t])
            # integrate input with past states
            net_in = np.dot(self.V, xt.T) + np.dot(self.U, s[t-1].T)
            s[t] = sigmoid(net_in)
            # compute hidden states
            net_out = np.dot(self.W, s[t].T)
            y[t] = softmax(net_out)
        return y,s
