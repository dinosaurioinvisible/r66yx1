
import numpy as np
# from copy import deepcopy
import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
# import plotly.graph_objects as go
import networkx as nx
from nu_fxs import *

def glx_anim(glx,world,show=True,save=False,autoclose=0,basic=False):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure(figsize=(16,8))
    # trial
    ax11 = fig.add_subplot(2,4,1)   # glider (anim)
    ax12 = fig.add_subplot(2,4,2)   # glider zoom (anim)
    ax13 = fig.add_subplot(2,4,3)   # glider trajectory (anim)
    ax14 = fig.add_subplot(2,4,4)   # cx,mx in states domain
    # genotype/history
    ax21 = fig.add_subplot(2,4,5)   # scatter gt
    ax22 = fig.add_subplot(2,4,6)   # env -> memb
    ax23 = fig.add_subplot(2,4,7)   # txs(dx) as trajectories/ env -> motion
    ax24 = fig.add_subplot(2,4,8)   # txs cx,mx in state domain

    tt = len(glx.states)
    if basic:
        envs = sum([len(set(i[1])) for i in glx.env_rxs.items()])
        fname = "basic glx, cys={}, motion={}, memb_rxs={}, core_rxs={}, envs={}".format(len(glx.cys),list(glx.motion),len(glx.memb_rxs),len(glx.core_rxs),envs)
    else:
        fname = "glx, known dashes={}, transients={}, gt size={}".format(len(glx.dxs),len(glx.txs),len(glx.exgt))
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")
    ax11.title.set_text("glider")
    ax12.title.set_text("zoom")

    # ax13: trajectory
    ax13.title.set_text("trajectory")
    glx_y = [100-l[0] for l in glx.loc]
    glx_x = [l[1] for l in glx.loc]
    y0,x0 = glx.loc[0]
    y0 = 100-y0
    ax13.set_xlim([min(glx_x)-5,max(glx_x)+5])
    ax13.set_ylim([min(glx_y)-5,max(glx_y)+5])
    ax13.plot(glx_x,glx_y,color="black")
    glx_xy = plt.Circle((x0,y0), radius=0.25, fill=True, color="green")
    ax13.add_patch(glx_xy)

    # ax14: cx states
    ax14.title.set_text("core transitions")
    # hmap = np.zeros((512,512)).astype(int)
    sxy = []
    sizes = []
    colors = []
    # i:cx0, j:cx
    for cx,cx0mx in glx.core_rxs.items():
        for cimi,nt in cx0mx.items():
            cx0,mx = cimi
            sxy.append([cx,cx0])
            sizes.append(nt)
            if (cx,0,0) in glx.cycles.keys():
                color = "black"
            elif nt>100:
                color = "red"
            elif nt>40:
                color = "orange"
            elif mx>0:
                color = "green"
            else:
                color = "blue"
            colors.append(color)
            #hmap[cx0][cx] += nt
    sx,sy = zip(*sxy)
    #ax14.imshow(hmap,cmap="hot",vmin=0,vmax=1,aspect="auto")
    ax14.scatter(sx,sy,c=colors,s=sizes,alpha=0.5)

    # ax21: gt input/gt responses
    ax21.title.set_text("genotype")
    xy = []
    if basic:
        xy = [[ri,rx] for ri,rx in enumerate(glx.exgt)]
    else:
        for gk in glx.exgt.keys():
            gv = int(''.join(str(i) for i in glx.exgt[gk]),2)
            xy.append([gk,gv])
        xy = sorted(xy)
    xs,ys = zip(*xy)
    ax21.scatter(xs,ys)

    # ax22: env/membrane
    if basic:
        n_env = sum([len(ei) for mi,ei in glx.memb_rxs.items()])
        ax22.title.set_text("env ({}) -> memb ({})".format(n_env,len(glx.memb_rxs)))
        ax22.set_xlim([-10,266])
        ax22.set_ylim([-10,266])
        mxy = []
        for mx,envx in glx.memb_rxs.items():
            for envi in envx:
                rei = reduce(envi,bin_pos=24)
                rmx = reduce(mx,bin_pos=16)
                mxy.append([rmx,rei])
        mx,my = zip(*mxy)
        colors = np.random.rand(len(mxy))
        ax22.scatter(mx,my,c=colors,alpha=0.5)

    # ax23
    if basic:
        # ax23: env/reaction
        ax23.title.set_text("env -> motion")
        # ax23.set_xlim([-0.5,4.5])
        ax23.set_ylim([-10,266])
        oxy = []
        for ox,envx in glx.env_rxs.items():
            for envi in envx:
                rei = reduce(envi,bin_pos=24)
                oxy.append([ox,rei])
        xo,xy = zip(*oxy)
        colors = np.random.rand(len(oxy))
        ax23.scatter(xo,xy,c=colors,alpha=0.5)

    # ax24 core -> core
    ax24.title.set_text("core transitions: graph")
    ax24.set_xlim([-5,515])
    ax24.set_ylim([-5,515])
    gx = nx.DiGraph()
    # cycles
    for c0st,cst in glx.cycles.items():
        cx0 = c0st[0]
        cx = cst[0]
        gx.add_node(cx,pos=(cx,cx0))
    for c0st,cst in glx.cycles.items():
        cx0 = c0st[0]
        cx = cst[0]
        gx.add_edge(cx0,cx,color="black")
    # core states
    for cx,cx0mx in glx.core_rxs.items():
        for cimi,nt in cx0mx.items():
            cx0,mx = cimi
            if cx not in gx.nodes:
                gx.add_node(cx,pos=(cx,cx0))
    # relevant edges
    for cx,cx0mx in glx.core_rxs.items():
        for cimi,nt in cx0mx.items():
            cx0,mx = cimi
            if cx0 not in gx.nodes:
                gx.add_node(cx0,pos=(cx0,0))
            if (cx0,cx) not in gx.edges and nt>25:
                if nt>100:
                    col = "red"
                elif nt>50:
                    col = "orange"
                else:
                    col = "blue"
                #col = "lightblue" if nt<100 else "red"
                gx.add_edge(cx0,cx,color=col)
    pos = nx.get_node_attributes(gx,"pos")
    colors = [gx[u][v]["color"] for u,v in gx.edges]
    # weights = [gx[u][v]["weight"] for u,v in gx.edges]
    # import pdb; pdb.set_trace()
    nx.draw(gx,pos,ax=ax24,node_size=0.5,node_color="black",alpha=0.2,with_labels=False,edge_color=colors,width=2,edge_cmap=plt.cm.Blues)

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
            gl_nav = ax11.imshow(wi_rgb)
            # gl domain
            gl_rgb = palette[gi.astype(int)]
            gl_domain = ax12.imshow(gl_rgb)
            # gl trajectory
            yi,xi = glx.loc[ti]
            yi = 100-yi
            glx_xy.center = (xi,yi)

        return gl_nav,gl_domain,glx_xy

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
