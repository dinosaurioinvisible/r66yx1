

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation

def glx_anim(glx_states,glx_fts,gt=None,fname=None,show=True,save=False):

    # subplots: nrows, ncols, index
    fig = plt.figure(figsize=[10,10],constrained_layout=False)

    # trials for the 4 initial configs
    glx_gs = fig.add_gridspec(3,4)
    # grid visualizations
    ax1 = fig.add_subplot(glx_gs[0,0])
    ax2 = fig.add_subplot(glx_gs[0,1])
    ax3 = fig.add_subplot(glx_gs[0,2])
    ax4 = fig.add_subplot(glx_gs[0,3])
    # imshow visualizations
    ax7 = fig.add_subplot(glx_gs[1,0])
    ax8 = fig.add_subplot(glx_gs[1,1])
    ax9 = fig.add_subplot(glx_gs[1,2])
    ax0 = fig.add_subplot(glx_gs[1,3])
    # genotype visualization
    gt_gs = fig.add_gridspec(3,1)
    ax5 = fig.add_subplot(gt_gs[2,0])

    # title
    if not fname:
        fname = "av_ft={}".format(glx_fts/len(glx_fts))
    fig.suptitle("{}".format(fname), ha="center", va="center")
    time = fig.text(0.5, 0.9, "", ha="center", va="center")
    # best time
    end_t = max([len(glx_st) for glx_st in glx_states])
    # number of cells
    n_cells = len(glx_states[0][0])

    # axs for grid visualization and paras
    axz=[ax1,ax2,ax3,ax4]
    major_ticks = np.arange(40, 61, 10)
    minor_ticks = np.arange(40, 61, 1)
    for i,axi in enumerate(axz):
        axi.set_title("c{}: ft={}".format(i+1,glx_fts[i]))
        axi.set_xlim(40,60)
        axi.set_ylim(40,60)
        axi.set_xticks(major_ticks)
        axi.set_yticks(major_ticks)
        axi.set_xticks(minor_ticks, minor=True)
        axi.set_yticks(minor_ticks, minor=True)
        axi.set_aspect("equal")
        axi.grid(which='both')
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)
    ax4.yaxis.tick_right()

    # axs for imshow visualization and params
    ax_ims=[ax7,ax8,ax9,ax0]
    for ei,axi in enumerate(ax_ims):
        axi.set_title("c{}: ft={}".format(i+5,glx_fts[ei]))
    plt.setp(ax8.get_yticklabels(), visible=False)
    plt.setp(ax9.get_yticklabels(), visible=False)
    ax0.yaxis.tick_right()

    # cells in grid
    cells = [[],[],[],[]]
    # cell plt objects for each axi
    for i,axi in enumerate(axz):
        for ci in range(n_cells):
            cx,cy = glx_states[i][0][ci][1:3]
            cell = plt.Circle((cx,cy),radius=0.5,color="grey",fill=True)
            axi.add_artist(cell)
            cells[i].append(cell)

    # genotype array
    rx=[]
    # for each cell in gt
    for ci in gt:
        rx_ci=np.zeros((512))
        # for each known response in ci
        for ri in gt[ci]:
            rx_ci[ri] = np.sum(gt[ci][ri])
        rx.append(rx_ci)
    # plot the arrays (colorbar is the same)
    ax5.set_yticks(np.arange(0,n_cells+1,1))
    gt_im1 = ax5.imshow(np.array(rx), aspect='auto')
    #plt.colorbar(gt_im2,ax=ax5,use_gridspec=True,orientation='horizontal')

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
        g1,g2,g3,g4 = glx_states
        print("\n\ng1,g2,g3,g4 = glx_states\n")
        import pdb; pdb.set_trace()

    # to start
    def init():
        return True

    def animate(i):
        time.set_text("time={}/{}".format(i,end_t-1))
        # (a) imshow visualization
        gmaps=[np.zeros((100,100)) for _ in range(5)]
        for cfg,axi in enumerate(ax_ims):
            # for those ended before
            if len(glx_states[cfg]) > i:
                states = glx_states[cfg][i]
                for ei,cell in enumerate(cells[cfg]):
                    ci,cx,cy,co,cst,cl = states[ei]
                    if cl==0:
                        cw=1
                    elif cst==1:
                        cw=3
                    else:
                        cw=2
                    gmaps[cfg][cx][cy]=cw
                gmaps[cfg] = np.rot90(gmaps[cfg],1)
                gm_i = axi.imshow(gmaps[cfg][40:61,40:61])
            else:
                axi.set_title("c{}: ft={}\n(dead t={})".format(cfg+1,round(glx_fts[cfg],2),len(glx_states[cfg])-1))
        # (b) grid visualization (same structure)
        for cfg,axi in enumerate(axz):
            # for those ended before
            if len(glx_states[cfg]) > i:
                states = glx_states[cfg][i]
                for ei,cell in enumerate(cells[cfg]):
                    ci,cx,cy,co,cst,cl = states[ei]
                    if cl==0:
                        cell_color="grey"
                    elif cst==1:
                        cell_color="green"
                    else:
                        cell_color="black"
                    cell.center=(cx,cy)
                    cell.set_color(cell_color)
            else:
                axi.set_title("c{}: ft={}\n(dead t={})".format(cfg+1,round(glx_fts[cfg],2),len(glx_states[cfg])-1))
        # big tuple for all cells
        all_cells = [cx for cxs in cells for cx in cxs]
        # return grid and imshow objects for now
        return tuple(all_cells)+tuple(gmaps)

    # call for onClick and for the animation
    fig.canvas.mpl_connect('button_press_event', onClick)
    anim=animation.FuncAnimation(fig, animate,
            init_func=init, frames=end_t, interval=1000, blit=False, repeat=True)

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









































#
