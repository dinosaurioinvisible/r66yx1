
# game of life fast implementation from https://github.com/thearn/game-of-life

from numpy.fft import fft2, ifft2, fftshift
import numpy as np

# 2d convolution, using FFT
def fft_convolve2d(x,y):
    fr = fft2(x)
    fr2 = fft2(np.flipud(np.flip(y)))
    m,n = fr.shape
    cc = np.real(ifft2(fr*fr2))
    cc = np.roll(cc, -int(m/2)+1, axis=0)
    cc = np.roll(cc, -int(n/2)+1, axis=1)
    return cc


# game of life transition
def gol_tx(state,k=None):
    # set kernel if not given
    if k==None:
        m,n = state.shape
        k = np.zeros((m,n))
        k[int(m/2)-1:int(m/2)+2,int(n/2)-1:int(n/2)+2] = np.array([[1,1,1],[1,0,1],[1,1,1]])
    print(k)
    # computes sums around each pixel
    b = fft_convolve2d(state,k).round()
    print(b)
    c = np.zeros(b.shape)
    c[np.where((b==2) & (state==1))] = 1
    # c[np.where(b==3)] = 1
    c[np.where((b==3) & (state==1))] = 1
    c[np.where((b==3) & (state==0))] = 1
    return c
