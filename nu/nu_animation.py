
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import plotly.graph_objects as go
import networkx as nx

def glx_anim(glx,world,show=True,save=False):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure()
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,1,2)

    fname = "glx recs={}".format(glx.recs)
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")

    # for the map of cycles
    ax3.set_xlim(0,512)
    ax3.set_ylim(0,512)
    transitions=[]
    for tx in glx.txs:
        txo = plt.Circle((tx[0],tx[1]),radius=10,color="orange",fill=True,visible=False)
        ax3.add_artist(txo)
        transitions.append(txo)
    hta,htb = zip(*glx.txs)
    ht0, = ax3.plot([],[],color="grey",linestyle="dashed")
    ht, = ax3.plot([],[],color="black",linestyle="dashed")

    # to pause the animation and check data
    anim_running = True
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True
        gl = glx
        print("\n\ngl = glider\n")
        import pdb; pdb.set_trace()

    # palette for imshow colors
    # 0:white, 1:blue, 2:red, 3:green, 4:black
    palette = np.array([[255,255,255],[0,0,255],[255,0,0],[0,255,0],[0,0,0]])

    def init():
        # trial response mapping
        for btx in glx.txs[:16]:
            bti = plt.Circle((btx[0],btx[1]),radius=5,color="blue",fill=True)
            ax3.add_artist(bti)
        # for i in range(0,4):
        #     for ci in range(1,5):
        #         btxi = ax3.plot(hta[:i*ci],htb[:i*ci],color="blue",linestyle="dashed")
        return True

    def animate(i):
        # title
        time.set_text("time={}/{}".format(i,len(glx.states)-1))
        # update
        if len(glx.states) > i:
            # glider imshow (if world objects: 4=black)
            wi = world*4
            # (0:off, 1:memb off, 2: memb on, 3:core on)
            gst = glx.states[i]+1
            gst[1:4,1:4] -= 1
            gst[1:4,1:4] *= 3
            # inverted cause of np array
            wi[int(glx.hi[i]-2):int(glx.hi[i]+3),int(glx.hj[i]-2):int(glx.hj[i]+3)] = gst
            gi = wi[int(glx.hi[i]-4):int(glx.hi[i]+5),int(glx.hj[i]-4):int(glx.hj[i]+5)]
            # colors
            wi_rgb = palette[wi.astype(int)]
            gl_nav = ax1.imshow(wi_rgb)
            # gl domain
            gl_rgb = palette[gi.astype(int)]
            gl_domain = ax2.imshow(gl_rgb)
            # map of cycles
            t0,t1 = max(0,i-2),max(0,i-1)
            ht0.set_data([hta[t0],hta[t1]],[htb[t0],htb[t1]])
            ht.set_data([hta[t1],hta[i]],[htb[t1],htb[i]])
            transitions[t1].set_color("orange")
            transitions[i].set_visible(True)
            transitions[i].set_color("black")

        return gl_nav,gl_domain,tuple(transitions),ht0,ht

    # call for onClick and for the animation
    fig.canvas.mpl_connect('button_press_event',onClick)
    anim=animation.FuncAnimation(fig, animate,
            init_func=init, frames=len(glx.states),
            interval=1000, blit=False, repeat=True)

    if save:
        # writer for saving the animation
        xwriter = animation.FFMpegWriter(fps=30)
        try:
            anim.save("{}.mp4".format(fname), writer=xwriter)
        except:
            # normally because of system required updates
            print('\ncouldn\'t save animation...\n')
    if show:
        plt.show()
    plt.close("all")


###
