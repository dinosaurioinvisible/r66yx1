
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import time

def trial_animation(trial, save=False):
    # nrows, ncols
    #fig = plt.figure(figsize=[10,10])
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    fig.suptitle("{}".format("simple agent trial", ha="center", va="center"))
    time = fig.text(0.5,0.92,"time=0")
    ax1.set_title("simple agent")
    ax1.set_xlim(0,trial.worldx)
    ax1.set_ylim(0,trial.worldy)
    ax1.set_aspect("equal")

    agents = []
    trajs = []
    irs = []
    for i in range(len(trial.agents)):
        ag, = ax1.plot([],[],color="blue")
        agents.append(ag)
        traj, = ax1.plot([],[],color="grey")
        trajs.append(traj)
        ag_irs = []
        for irx in trial.agents[i].sensors.ir_sensors:
            ir, = ax1.plot([],[],color="orange")
            ag_irs.append(ir)
        irs.append(ag_irs)

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
        xt = trial
        print("\nxt = trial object\n")
        import pdb; pdb.set_trace()

    # fixed background
    def init():
        for tree in trial.trees:
            ax1.plot(*tree.area.exterior.xy, color="green")

        return True

    # animation
    def animate(i):
        # according to number of savings
        time.set_text("time={}".format(i))
        # agent
        for enum,ag in enumerate(trial.agents):
            agent_loc = Point(ag.data.x[i],ag.data.y[i])
            agent_body = agent_loc.buffer(ag.data.r)
            agents[enum].set_data(*agent_body.exterior.xy)
            trajs[enum].set_data(ag.data.x[:i],ag.data.y[:i])
            ix = [ir for ir in ag.data.irs[i] if ir]
            for n_ir,ir in enumerate(ix):
                irs[enum][n_ir].set_data(*ir.exterior.xy)
        all_irs = [ir for irx in irs for ir in irx]

        return tuple(agents),tuple(trajs),tuple(all_irs)

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
            init_func=init, frames=trial.t, interval=100, blit=False, repeat=False)

    if save:
        # writer for saving the animation
        xwriter = animation.FFMpegWriter(fps=30)
        try:
            anim.save("{}.mp4".format(fname), writer=xwriter)
        except:
            print('\ncouldn\'t save animation...')
    plt.show()







































###
