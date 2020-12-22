
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import time


def sim_animation(evaluation, show=True, save=False, fname=None):
    # nrows, ncols, index
    fig = plt.figure(figsize=[12,12])
    # best
    ax1 = fig.add_subplot(2,2,1)
    # remaining alphas
    ax2 = fig.add_subplot(4,4,3)
    ax3 = fig.add_subplot(4,4,4)
    ax4 = fig.add_subplot(4,4,7)
    ax5 = fig.add_subplot(4,4,8)
    # ft parameter values
    ax6 = fig.add_subplot(4,2,5)
    # genotype
    ax7 = fig.add_subplot(2,4,7)
    # network
    ax8 = fig.add_subplot(2,4,8)
    # ax9 ??
    ax9 = fig.add_subplot(4,2,7)

    # best trial, and the remaining alphas
    genotype = evaluation.genotype
    best_trial = evaluation.trials[0]
    best_trial_time = len(best_trial.data_ft)
    # sorted remaining (different alphas)
    alphas = [best_trial.alpha]
    rm_trials = []
    for trial in evaluation.trials[1:]:
        if trial.alpha not in alphas:
            alphas.append(trial.alpha)
            rm_trials.append(trial)

    # text above
    fig.suptitle("{}".format(fname), ha="center", va="center")
    time = fig.text(0.5, 0.92, "time=0".format(best_trial.ft), ha="center", va="center")

    # ax1: basics, objects for agents and ir sensors
    ax1.set_title("alpha={}, ft={}".format(np.round(np.degrees(best_trial.alpha),2),np.round(best_trial.ft),2))
    ax1.set_xlim(-100,100)
    ax1.set_ylim(-100,100)
    ax1.set_aspect("equal")
    agents = []
    ag_colors = ["blue","green","red"]
    trajs = []
    irs = []
    for i in range(len(best_trial.agents)):
        ag, = ax1.plot([],[],color="black")
        agents.append(ag)
        ag_irs = []
        traj, = ax1.plot([],[],color=ag_colors[i])
        trajs.append(traj)
        for irx in best_trial.agents[i].sensors.irx:
            if irx:
                ir, = ax1.plot([],[], color="black")
                ag_irs.append(ir)
        irs.append(ag_irs)
    ags, = ax1.plot([],[], color="grey", linestyle="dashed")
    centroid, = ax1.plot([],[], marker="x", color="grey")

    # ax2-5: centroids, space and text
    ax2.set_title("alpha={}, ft={}".format(np.round(np.degrees(evaluation.trials[1].alpha)),np.round(evaluation.trials[1].ft),2))
    ax2.set_xlim(-60,60)
    ax2.set_ylim(-60,60)
    cent2, = ax2.plot([],[], marker="x", color="black")
    ax2.tick_params(axis="y",which="both",left=False,right=True,labelleft=False)
    ax3.set_title("alpha={}, ft={}".format(np.round(np.degrees(evaluation.trials[2].alpha)),np.round(evaluation.trials[2].ft),2))
    ax3.set_xlim(-60,60)
    ax3.set_ylim(-60,60)
    cent3, = ax3.plot([],[], marker="x", color="black")
    ax4.set_title("alpha={}, ft={}".format(np.round(np.degrees(evaluation.trials[3].alpha)),np.round(evaluation.trials[3].ft),2),y=-0.18)
    ax4.set_xlim(-60,60)
    ax4.set_ylim(-60,60)
    ax4.tick_params(axis="x",which="both",bottom=False,top=True,labelbottom=False)
    ax4.tick_params(axis="y",which="both",left=False,right=True,labelleft=False)
    cent4, = ax4.plot([],[], marker="x", color="black")
    ax5.set_title("alpha={}, ft={}".format(np.round(np.degrees(evaluation.trials[4].alpha)),np.round(evaluation.trials[4].ft),2),y=-0.18)
    ax5.set_xlim(-60,60)
    ax5.set_ylim(-60,60)
    ax5.tick_params(axis="x",which="both",bottom=False,top=True,labelbottom=False)
    cent5, = ax5.plot([],[], marker="x", color="black")

    # ax7: network neural space
    ax7.set_xlim(0,200)
    ax7.set_ylim(0,250)
    ax7.tick_params(axis="y",which="both",left=False,right=True,labelleft=False)
    # ax8: network
    ax8.set_xlim(0,200)
    ax8.set_ylim(0,250)

    # ax6: plot dist,maxdist, gt, cp, ft
    ax6.set_xlim(0,best_trial_time)
    ax6.set_ylim(0,1.01)
    tbar, = ax6.plot([],[],color="black")
    # ax9: plot d0,d1,d2, st,stft, gt
    ax9.set_xlim(0,best_trial_time)
    ax6.set_ylim(0,1.01)
    tbar, = ax6.plot([],[],color="black")

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
        xt = best_trial
        print("\nxt = trial object\n")
        import pdb; pdb.set_trace()


    def init():
        # remaining alphas trajectories (ax2-ax5)
        for enum,xag in enumerate(rm_trials[0].agents):
            ax2.plot(xag.data.x,xag.data.y, color=ag_colors[enum])
        for enum,xag in enumerate(rm_trials[1].agents):
            ax3.plot(xag.data.x,xag.data.y, color=ag_colors[enum])
        for enum,xag in enumerate(rm_trials[2].agents):
            ax4.plot(xag.data.x,xag.data.y, color=ag_colors[enum])
        for enum,xag in enumerate(rm_trials[3].agents):
            ax5.plot(xag.data.x,xag.data.y, color=ag_colors[enum])

        # ax6
        # ycp = [cp[1] for cp in best_trial.data_cp]
        cpx = [cp[0] for cp in best_trial.data_cp]+[best_trial_time]
        cpy = [cp[1] for cp in best_trial.data_cp]+[best_trial.data_cp[-1][1]]
        ax6.plot(cpx,cpy, label="cp")
        # gt, st, ft
        ygt = [gt[2] for gt in best_trial.data_gt]
        ystft = [st[4]/3 for st in best_trial.data_st]
        yft = [ft[1]/120 for ft in best_trial.data_ft]
        ax6.plot(ygt, label="gt")
        ax6.plot(ystft, label="stft/3")
        ax6.plot(yft, label="ft/max(ft)")
        ax6.legend()

        # ax9
        #

        # ax7: sensor and motor regions
        ax7.plot([0,200],[50,50],color="black")
        ax7.plot([0,200],[220,220], color="black")
        for sx in evaluation.nx_space.sregion:
            ax7.plot(*sx.area.exterior.xy, color="black")
        for mx in evaluation.nx_space.mregion:
            ax7.plot(*mx.area.exterior.xy, color="black")
        # from genotype
        for nx in evaluation.network:
            # neural region
            npoint = plt.Circle((nx.x,nx.y), radius=1, fill=True, color="black")
            ax7.add_patch(npoint)
            ax7.plot(*nx.area.exterior.xy, color="black")
            # input connections
            for ci in nx.l_in:
                lst = "dashed" if ci[2] < 0 else "solid"
                ax7.plot([ci[0],nx.x],[ci[1],nx.y],color="blue", linestyle=lst)
            # output connections
            for co in nx.l_out:
                lst = "dashed" if co[2] < 0 else "solid"
                ax7.plot([nx.x,co[0]],[nx.y,co[1]],color="red", linestyle=lst)

        # ax8: actual network
        ax8.plot([0,200],[50,50],color="black")
        ax8.plot([0,200],[220,220], color="black")
        for sx in evaluation.nx_space.sregion:
            ax8.plot(*sx.area.exterior.xy, color="black")
        for mx in evaluation.nx_space.mregion:
            ax8.plot(*mx.area.exterior.xy, color="black")
        # from genotype (only working connections)
        for nx in evaluation.network:
            # neurons
            npoint = plt.Circle((nx.x,nx.y), radius=1, fill=True, color="black")
            ax8.add_patch(npoint)
            ax8.plot(*nx.area.exterior.xy, color="black")
            # input connections
            for i in range(len(nx.cx_in)):
                if nx.cx_in[i]:
                    ci = nx.l_in[i]
                    lst = "dashed" if ci[2] < 0 else "solid"
                    ax8.plot([ci[0],nx.x],[ci[1],nx.y],color="blue", linestyle=lst)
            # output connections
            for o in range(len(nx.cx_out)):
                if nx.cx_out[o]:
                    co = nx.l_out[o]
                    lst = "dashed" if co[2] < 0 else "solid"
                    ax8.plot([nx.x,co[0]],[nx.y,co[1]],color="red", linestyle=lst)
        return True


    def animate(i):
        # i: from number of savings in trial
        time.set_text("time={}".format(i))
        # at: adjusted i for savings from agents' states
        at = int(i/evaluation.dt)
        # main centroid and triangle
        centroid.set_data(best_trial.triangles[i].centroid.xy)
        ags.set_data(*best_trial.triangles[i].exterior.xy)
        # remaining centroids (can be shorter)
        if i < len(rm_trials[0].triangles):
            cent2.set_data(rm_trials[0].triangles[i].centroid.xy)
        if i < len(rm_trials[1].triangles):
            cent3.set_data(rm_trials[1].triangles[i].centroid.xy)
        if i < len(rm_trials[2].triangles):
            cent4.set_data(rm_trials[2].triangles[i].centroid.xy)
        if i < len(rm_trials[3].triangles):
            cent5.set_data(rm_trials[3].triangles[i].centroid.xy)
        # ax1 agents
        for enum,ag in enumerate(best_trial.agents):
            # agent body
            agents[enum].set_data(*ag.data.body[at].exterior.xy)
            # trajectories
            trajs[enum].set_data(ag.data.x[:at],ag.data.y[:at])
            # sensors
            ag_irs = [ir for ir in ag.data.irs[at] if ir]
            for n_ir,ir in enumerate(ag_irs):
                irs[enum][n_ir].set_data(*ir.xy)
        all_irs = [ir for irx in irs for ir in irx]
        # time mark for ax6
        tbar.set_data([i,i],[0,1])

        #import pdb; pdb.set_trace()
        return centroid,ags,traj, tuple(agents)+tuple(all_irs)

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
            init_func=init, frames=best_trial_time, interval=10, blit=False, repeat=False)

    if save:
        # writer for saving the animation
        xwriter = animation.FFMpegWriter(fps=30)
        try:
            anim.save("{}.mp4".format(fname), writer=xwriter)
        except:
            print('\ncouldn\'t save animation...')
    if show:
        plt.show()
    plt.close("all")


























#
