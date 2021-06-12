
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import plotly.graph_objects as go
import networkx as nx

def glx_anim(glx,world,show=True,save=False,autoclose=0):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure(figsize=(12,10))
    ax1 = fig.add_subplot(3,2,1)    # anim: glider
    ax2 = fig.add_subplot(3,2,2)    # anim: glider zoom
    ax3 = fig.add_subplot(3,2,3)    # gt network (memb/core)
    ax4 = fig.add_subplot(3,2,4)    # gt loops and txs
    ax5 = fig.add_subplot(3,2,5)    # trial sts (core,memb,loops)
    ax6 = fig.add_subplot(3,2,6)    # gl responses to dashes

    tt = len(glx.states)
    fname = "glx, known dashes={}, cycles={}, transients={}".format(tt,len(self.dashes),len(glx.cycles),len(glx.txs))
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")
    ax1.title.set_text("glider")
    ax2.title.set_text("zoom")
    ax3.title.set_text("gt: memb/core")
    ax4.title.set_text("gt: cycles and transients")
    ax5.title.set_text("trial states")
    ax6.title.set_text("responses to dashes")

    # ax3: memb/core
    gx = nx.DiGraph()
    for ri in glx.rxs.keys():
        rxs = glx.rxs[ri]
        ci,mi,di = ri
        gx.add_node((ci,mi),pos=(ci,mi))
        for rx in rxs:
            cx,mx,dij = rx
            gx.add_node((cx,mx),pos=(cx,mx))
            gx.add_edge((ci,mi),(cx,mx))
    nx.draw_networkx(gx,ax=ax3,node_size=10,alpha=0.5,with_labels=False)

    # ax4: loops & transients
    gx2 = nx.DiGraph()
    # for each mapping
    for (ci,mi,di) in glx.cycles.keys():
        # starting node (key)
        if (ci,mi) not in gx2.nodes:
            gx2.add_node((ci,mi),pos=(ci,mi))
        # ending node (dict value)
        cx,mx = glx.cycles[(ci,mi,di)]
        if (cx,mx) not in gx2.nodes:
            gx2.add_node((cx,mx),pos=(cx,mx))
        gx2.add_edge((ci,mi),(cx,mx),color="b")
    # connecting transients
    for dash in glx.txs.keys():
        tx_seqs = glx.txs[dash]
        for tx_seq in tx_seqs:
            for ti in range(1,len(tx_seq)):
                cti,mti,dti = tx_seq[ti]
                if (cti,mti) not in gx2.nodes:
                    gx2.add_node((cti,mti),pos=(cti,mti))
                ct0,mt0 = tx_seq[ti-1]
                gx2.add_edge((ct0,mt0),(cti,mti),color="r")
    colors = [gx2[u][v]['color'] for u,v in gx2.edges]
    nx.draw_networkx(gx2,ax=ax4,node_size=10,alpha=0.5,with_labels=False,edge_color=colors)

    # ax5: trials states
    ax5.plot(glx.core, label="core sts", color="black")
    ax5.plot(glx.memb, label="memb sts", color="grey")
    for loop in glx.loops:
        ax5.plot(loop[0], linestyle="dashed", color="blue")
        ax5.plot(loop[1], linestyle="dashed", color="red")
        ax5.plot(loop[2], linestyle="dashed", color="green")
    ax5.legend()

    # ax6: responses to dashes
    ax6.plot(glx.env, label="dashes", color="black")
    ax6.plot(glx.dxy, label="motion", color="blue")
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

    def animate(ti):
        time.set_text("time={}/{}".format(ti,tt-1))
        # update
        if ti < tt:
            # glider imshow (if world objects: 4=black)
            wi = world*4
            # (0:off, 1:memb off, 2: memb on, 3:core on)
            gst = glx.states[ti]+1
            gst[1:4,1:4] -= 1
            gst[1:4,1:4] *= 3
            # inverted cause np array
            i,j = glx.loc[ti][:2]
            wi[i-2:i+3,j-2:j+3] = gst
            gi = wi[i-4:i+5,j-4:j+5]
            # colors
            wi_rgb = palette[wi.astype(int)]
            gl_nav = ax1.imshow(wi_rgb)
            # gl domain
            gl_rgb = palette[gi.astype(int)]
            gl_domain = ax2.imshow(gl_rgb)

        return gl_nav,gl_domain

    # call for onClick and for the animation
    fig.canvas.mpl_connect('button_press_event',onClick)
    anim=animation.FuncAnimation(fig, animate,
            init_func=init, frames=tt,
            interval=500, blit=False, repeat=True)

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
