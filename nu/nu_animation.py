
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation

def glx_anim(glx,world,show=True,save=False):

    # fig and subplots: nrows, ncols, index
    fig = plt.figure()
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,1,2)
    fname = "glx ft={}".format(glx.ft)
    fig.suptitle("{}".format(fname),ha="center",va="center")
    time = fig.text(0.5,0.95,"",ha="center",va="center")

    # for the map of cycles
    ax3.set_xlim(0,512)
    ax3.set_ylim(0,512)
    transitions=[]
    for hi in range(len(glx.hb)-1):
        tx = glx.hb[hi]
        ty = glx.hb[hi+1]
        t12 = plt.Circle((tx,ty),radius=10,color="orange",fill=True,visible=False)
        ax3.add_artist(t12)
        transitions.append(t12)
    htx = glx.hb[:-1]
    hty = glx.hb[1:]
    ht, = ax3.plot([],[],color="black",linestyle="dashed")
    ht2, = ax3.plot([],[],color="grey",linestyle="dashed")

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
        for bt in glx.basal_txs:
            bti = plt.Circle((bt[0],bt[1]),radius=5,color="blue",fill=True)
            ax3.add_artist(bti)
        return True

    def animate(ti):
        # title
        time.set_text("time={}/{}".format(ti,len(glx.states)-1))
        # update
        if len(glx.states) > ti:
            # glider imshow (if world objects: 4=black)
            wi = world*4
            # (0:off, 1:memb off, 2: memb on, 3:core on)
            gst = glx.states[ti].reshape(5,5)+1
            gst[1:4,1:4] -= 1
            gst[1:4,1:4] *= 3
            # inverted cause of np array
            wi[int(glx.hi[ti]-2):int(glx.hi[ti]+3),int(glx.hj[ti]-2):int(glx.hj[ti]+3)] = gst
            gi = wi[int(glx.hi[ti]-4):int(glx.hi[ti]+5),int(glx.hj[ti]-4):int(glx.hj[ti]+5)]
            # colors
            wi_rgb = palette[wi.astype(int)]
            gl_nav = ax1.imshow(wi_rgb)
            # gl domain
            gl_rgb = palette[gi.astype(int)]
            gl_domain = ax2.imshow(gl_rgb)
            # map of cycles
            if len(transitions)-1 > ti:
                #transitions[ti-1].set_visible(False)
                transitions[ti].set_visible(True)
                t0,t1 = max(0,ti-2), max(0,ti-1)
                ht.set_data(htx[t1:ti+1],hty[t1:ti+1])
                ht2.set_data(htx[t0:ti],hty[t0:ti])
        return gl_nav,gl_domain,tuple(transitions),ht,ht2

    # call for onClick and for the animation
    fig.canvas.mpl_connect('button_press_event', onClick)
    anim=animation.FuncAnimation(fig, animate,
            init_func=init, frames=len(glx.states), interval=1000, blit=False, repeat=True)

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
