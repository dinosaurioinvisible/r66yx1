
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
    ax1 = fig.add_subplot(3,2,1)    # anim: glider
    ax2 = fig.add_subplot(3,2,2)    # anim: glider zoom
    ax3 = fig.add_subplot(3,2,3)    # gt network (memb/core)
    ax4 = fig.add_subplot(3,2,4)    # gt loops and txs
    ax5 = fig.add_subplot(3,2,5)    # trial sts (core,memb,loops)
    ax6 = fig.add_subplot(3,2,6)    # gl responses to dashes

    tt = len(glx.states)
    fname = "glx timesteps={}, known dashes={}, cycles={}".format(tt,len(glx.kdp),len(glx.cycles))
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
        di,ci,mi = ri
        gx.add_node((ci,mi),pos=(ci,mi))
        for rx in rxs:
            dx,cx,mx = rx
            gx.add_node((cx,mx),pos=(cx,mx))
            gx.add_edge((ci,mi),(cx,mx))
    nx.draw_networkx(gx,ax=ax3,node_size=10,alpha=0.5,with_labels=False)

    # ax4: loops & transients
    gx2 = nx.DiGraph()
    # loops
    for cycle_i in glx.cycles.keys():
        ci,mi = cycle_i
        if (ci,mi) not in gx2.nodes:
            gx2.add_node((ci,mi),pos=(ci,mi))
        # create only the first (to avoid overlaps)
        cx,mx = glx.cycles[cycle_i][0]
        if (cx,mx) not in gx2.nodes:
            gx2.add_node((cx,mx),pos=(cx,mx))
        gx2.add_edge((ci,mi),(cx,mx),color="b")
    # connecting transients
    for tx in glx.txs.keys():
        (c0,m0),(cx,mx) = tx
        tx_seq = glx.txs[tx]
        for ti,tx_st in enumerate(tx_seq):
            ci,mi = tx_st
            if (ci,mi) not in gx2.nodes:
                gx2.add_node((ci,mi),pos=(ci,mi))
            if ti>0:
                c0,m0 = tx_seq[ti-1]
                gx2.add_edge((c0,m0),(ci,mi),color="r")
    colors = [gx2[u][v] for u,v in gx2.edges]
    nx.draw_networkx(gx,ax=ax4,node_size=10,alpha=0.5,with_labels=False,edge_color=color)

    # ax5: trials states
    ax5.plot(glx.core, label="core sts", color="black")
    ax5.plot(glx.memb, label="memb sts", color="grey")
    for loop in glx.loops:
        ax5.plot(loop[0], linestyle="dashed")
        ax5.plot(loop[1], linestyle="dashed")
    ax5.legend()

    # ax6: responses to dashes
    for ri in glx.rxs.keys():
        di,ci,mi = ri
        for rx in glx.rxs[ri]:
            dx,cx,mx = rx
            ax6.plot([ci,cx],[di,dx],color="black")

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

        return gl_nav,gl_domain

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
