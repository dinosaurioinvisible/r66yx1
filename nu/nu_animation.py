
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import plotly.graph_objects as go
import networkx as nx
from nu_fxs import reduce

def glx_anim(glx,world,show=True,save=False,autoclose=0):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure(figsize=(16,10))
    # trial
    ax11 = fig.add_subplot(2,4,1)   # glider (anim)
    ax12 = fig.add_subplot(2,4,2)   # glider zoom (anim)
    ax13 = fig.add_subplot(2,4,3)   # glider trajectory
    ax14 = fig.add_subplot(2,4,4)   # cx,mx in states domain
    # genotype
    ax21 = fig.add_subplot(2,4,5)   # exgt as ein,erx array
    ax22 = fig.add_subplot(2,4,6)   #
    ax23 = fig.add_subplot(2,4,7)   # txs(dx) as trajectories
    ax24 = fig.add_subplot(2,4,8)   # txs cx,mx in state domain

    tt = len(glx.states)
    fname = "glx, known dashes={}, transients={}, gt size={}".format(len(glx.dxs),len(glx.txs),len(glx.exgt))
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")
    ax11.title.set_text("glider")
    ax12.title.set_text("zoom")
    ax13.title.set_text("trajectory")
    ax14.title.set_text("cx,mx states")
    ax21.title.set_text("genotype")
    ax22.title.set_text("gt: ")
    ax23.title.set_text("gt: txs trajectories")
    ax24.title.set_text("gt: cx,mx states")

    # ax13: trajectory
    glx_y = [100-l[0] for l in glx.loc]
    glx_x = [l[1] for l in glx.loc]
    #ax13.set_xlim([0,100])
    #ax13.set_ylim([0,100])
    ax13.plot(glx_x,glx_y,color="grey")

    # ax14: cx,mx states; ax24: cx,mx gt states
    gx1 = nx.DiGraph()
    gx2 = nx.DiGraph()
    # cycles locations
    p0 = np.array([[0,50,50,50,50,0,0,0]]).reshape(4,2)
    p1 = p0.astype(int)
    p1[:,0] += 512+100
    p2 = p0.astype(int)
    p2[:,1] += 512+100
    p3 = p0+512+100
    pxy = [p0,p1,p2,p3]
    for i,ck in enumerate(glx.cycles.keys()):
        cx,mx,ex = ck
        px,py = pxy[int(i/4)][i%4]
        gx1.add_node((cx,mx),pos=(px,py))
        gx2.add_node((cx,mx),pos=(px,py))
    for ck in glx.cycles.keys():
        cx0,mx0,dx0 = ck
        cx,mx = glx.cycles[cx0,mx0,dx0]
        gx1.add_edge((cx0,mx0),(cx,mx),color="b")
        gx2.add_edge((cx0,mx0),(cx,mx),color="b")
    # cx,mx trial states
    for i,[ci,mi,ei] in enumerate(zip(glx.core_sts,glx.memb_sts,glx.env_sts)):
        if (ci,mi,ei) not in glx.cycles.keys():
            px = ci+100
            mri = reduce(mi)
            py = (mri*2)+100
            gx1.add_node((ci,mi),pos=(px,py))
            if i>0:
                c0 = glx.core_sts[i-1]
                m0 = glx.memb_sts[i-1]
                gx1.add_edge((c0,m0),(ci,mi),color="r")
    pos1 = nx.get_node_attributes(gx1,"pos")
    colors1 = [gx1[u][v]['color'] for u,v in gx1.edges]
    nx.draw(gx1,pos1,ax=ax14,node_size=10,alpha=0.5,with_labels=False,edge_color=colors1)
    # cx,mx genotype txs
    for tk in glx.txs.keys():
        transients = glx.txs[tk]
        for transient in transients:
            for sti in transient[:-1]:
                cx0 = sti[0]
                mx0 = sti[1]
                dxo = sti[2]
                cx = sti[6]
                mx = sti[7]
                if (cx,mx) not in gx2.nodes:
                    px = cx+100
                    mri = reduce(mx)
                    py = (mri*2)+100
                    gx2.add_node((cx,mx),pos=(px,py))
                if ((cx0,mx0),(cx,mx)) not in gx2.edges:
                    gx2.add_edge((cx0,mx0),(cx,mx),color="r")
    pos2 = nx.get_node_attributes(gx2,"pos")
    colors2 = [gx2[u][v]['color'] for u,v in gx2.edges]
    nx.draw(gx2,pos2,ax=ax24,node_size=10,alpha=0.2,with_labels=False,edge_color=colors2)

    # ax21: gt as array
    xy = []
    for gk in glx.exgt.keys():
        gv = int(''.join(str(i) for i in glx.exgt[gk]),2)
        xy.append([gk,gv])
    xy = sorted(xy)
    xs,ys = zip(*xy)
    ax21.scatter(xs,ys)

    # ax23: txs as trajectories
    for tk in glx.txs.keys():
        transients = glx.txs[tk]
        for transient in transients:
            x,y = 50,50
            xs = [x]
            ys = [y]
            om0 = transient[0][3]
            if om0==1:
                x += 1
            elif om0==2:
                y -= 1
            elif om0==3:
                x -= 1
            elif om0==4:
                y += 1
            xs.append(x)
            ys.append(y)
            for sti in transient[:-1]:
                om = sti[5]
                if om==1:
                    x += 1
                elif om==2:
                    y -= 1
                elif om==3:
                    x -= 1
                elif om==4:
                    y += 1
                xs.append(x)
                ys.append(y)
        ax23.plot(xs,ys)

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
