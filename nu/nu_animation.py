
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import plotly.graph_objects as go
import networkx as nx

def glx_anim(glx,world,show=True,save=False):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure(figsize=(10,10))
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    ax4 = fig.add_subplot(2,2,4)

    fname = "glx timesteps={}, known dashes={}, cycles={}".format(len(glx.states),len(glx.kdp),len(glx.cycles))
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")

    # transitions during trial
    ax3.set_xlim(0,512)
    ax3.set_ylim(0,512)
    transitions=[]
    for hi in range(len(glx.hs)-1):
        tst = plt.Circle((glx.hs[hi],glx.hs[hi+1]),radius=5,color="blue",fill=True,visible=False)
        ax3.add_artist(tst)
        transitions.append(tst)
    tx0, = ax3.plot([],[],color="grey",linestyle="dashed")
    tx1, = ax3.plot([],[],color="black",linestyle="dashed")

    # graph of cycles
    gk = nx.DiGraph()
    for cxi in glx.cycles:
        for i,cx in enumerate(cxi):
            gk.add_node(cx,pos=(cx,???))
            if i>0:
                gk.add_edge(cxi[i-1],cx)
    nx.draw_networkx(gk,ax=ax4,node_size=10,alpha=0.25)

    # graph of transitions
    # gx = nx.DiGraph()
    # for txi in glx.txs:
    #     for i,tx in enumerate(txi):
    #         gx.add_node(tx,pos=(tx,???))
    #         if i>0:
    #             gx.add_edge(txi[i-1],tx)
    # nx.draw_networkx(gx,ax=ax4,node_size=10,alpha=0.25)
    # nx.draw(gx,ax=ax4)

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
        # loops nodes and edges
        # for cycle in glx.cycles:
        #     loop = cycle+[cycle[:2]]
        #     for ci in range(len(cycle)-2):
        #         node = plt.Circle((loop[ci],loop[ci+1]),radius=10,color="orange",fill=True)
        #         ax3.add_artist(node)
        #         edge = ax3.plot([loop[ci],loop[ci+1]],[loop[ci+1],loop[ci+2]],color="orange",linestyle="dashed")
        return True

    def animate(i):
        # title
        time.set_text("time={}/{}".format(i,len(glx.states)-1))
        # update
        if i < len(glx.states):
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
            # transition path
            if i < len(transitions):
                transitions[i].set_visible(True)
            if 0 < i < len(transitions):
                tx1.set_data([glx.hs[i-1:i+1]],[glx.hs[i:i+2]])
            if i > 1:
                tx0.set_data([glx.hs[i-2:i]],[glx.hs[i-1:i+1]])

        return gl_nav,gl_domain,tuple(transitions),tx0,tx1

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
