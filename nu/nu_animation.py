
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import plotly.graph_objects as go
import networkx as nx

def glx_anim(glx,world,show=True,save=False,autoclose=0):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure(figsize=(15,10))
    ax1 = fig.add_subplot(3,2,1)    # glider
    ax2 = fig.add_subplot(3,2,2)    # glider zoom
    ax3 = fig.add_subplot(3,2,3)    # genotype transitions
    ax4 = fig.add_subplot(3,2,4)    # trial transitions
    ax5 = fig.add_subplot(3,2,5)    # gt cycles
    ax6 = fig.add_subplot(3,2,6)    # trial cycles

    tt = len(glx.states)
    fname = "glx timesteps={}, known dashes={}, cycles={}".format(tt,len(glx.kdp),len(glx.cycles))
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")
    ax1.title.set_text("glider")
    ax2.title.set_text("zoom")
    ax3.title.set_text("genotype transitions")
    ax4.title.set_text("trial transitions")
    ax5.title.set_text("genotype cycles")
    ax6.title.set_text("trial cycles")

    # ax3: gt transitions (graph)
    gx = nx.DiGraph()
    for txi in glx.txs:
        for i,tx in enumerate(txi):
            gx.add_node(tx)
            if i>0:
                gx.add_edge(txi[i-1],tx)
    nx.draw_networkx(gx,ax=ax3,node_size=10,alpha=0.5)

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

    # ax5: gt cycles (graph)
    gk = nx.DiGraph()
    for cxi in glx.cycles:
        for i,cx in enumerate(cxi):
            gk.add_node(cx)
            if i>0:
                gk.add_edge(cxi[i-1],cx)
    nx.draw_networkx(gk,ax=ax5,node_size=10,alpha=0.5)

    # ax6: trial cycles (regular plt)
    ax6.plot(glx.hs, label="trial loops",color="black")
    colors = ["purple","blue","green","orange","red"]
    for cx in glx.hcycles:
        cxlen=0
        for i in cx:
            if i!=0:
                cxlen+=1
            if cxlen>1 and i==0:
                break
        color = colors[cxlen-3]
        ax6.plot(cx,color=color,label="{}".format(cxlen))
    ax6.legend()

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
        return True

    def animate(i):
        time.set_text("time={}/{}".format(i,tt-1))
        # update
        if i < tt:
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
            if i < len(txs):
                txs[i].set_visible(True)
                if i > 0:
                    tx1.set_data([glx.hs[i-1:i+1]],[glx.hs[i:i+2]])
                if i > 1:
                    tx0.set_data([glx.hs[i-2:i]],[glx.hs[i-1:i+1]])

        return gl_nav,gl_domain,tuple(txs),tx0,tx1

    # call for onClick and for the animation
    fig.canvas.mpl_connect('button_press_event',onClick)
    anim=animation.FuncAnimation(fig, animate,
            init_func=init, frames=tt,
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
        if autoclose>0:
            plt.show(block=False)
            plt.pause(autoclose)
            plt.close("all")
        else:
            plt.show()


###
