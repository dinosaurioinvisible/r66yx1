
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import ag_trial
import time

def trial_animation(ob,save=False):
    # check for trial or genotype
    if isinstance(ob,ag_trial.Trial):
        trial = ob
    else:
        trial = ag_trial.Trial()
        trial.run_trial(ob)

    # define figure
    fig = plt.figure() #plt.figure(figsize=[10,10])
    # nrows, ncols
    ax1 = fig.add_subplot(1,1,1)
    fig.suptitle("{}".format("simple agent trial", ha="center", va="center"))
    time = fig.text(0.5,0.92,"time=0")
    ax1.set_title("simple agent")
    ax1.set_xlim(0,trial.worldx)
    ax1.set_ylim(0,trial.worldy)
    ax1.set_aspect("equal")

    # create plot objects
    agents = []
    trajs = []
    irs = []
    fas = []
    for i in range(len(trial.agents)):
        ag, = ax1.plot([],[],color="black")
        agents.append(ag)
        traj, = ax1.plot([],[],color="grey")
        trajs.append(traj)
        ag_irs = []
        for irx in trial.agents[i].sensors.ir_sensors:
            ir, = ax1.plot([],[],color="orange")
            ag_irs.append(ir)
        irs.append(ag_irs)
        fa, = ax1.plot([],[],color="blue")
        fas.append(fa)

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
        time.set_text("time={}".format(i+1))
        # agent
        for enum,ag in enumerate(trial.agents):
            # agent body
            agent_loc = Point(ag.data.x[i],ag.data.y[i])
            agent_body = agent_loc.buffer(ag.data.r)
            agents[enum].set_data(*agent_body.exterior.xy)
            # trajectory
            trajs[enum].set_data(ag.data.x[:i+1],ag.data.y[:i+1])
            # ir sensors
            ix = [ir for ir in ag.data.irs[i] if ir]
            for n_ir,ir in enumerate(ix):
                irs[enum][n_ir].set_data(*ir.exterior.xy)
            # feeding areas
            fx = ag.data.x[i] + (ag.data.r+ag.data.f_range/2)*np.sin(ag.data.o[i])
            fy = ag.data.y[i] + (ag.data.r+ag.data.f_range/2)*np.cos(ag.data.o[i])
            floc = Point(fx,fy)
            f_area = floc.buffer(ag.data.f_range/2)
            fas[enum].set_data(*f_area.exterior.xy)
        # same tuple for all irs of all agents
        all_irs = [ir for irx in irs for ir in irx]

        return tuple(agents),tuple(trajs),tuple(all_irs),tuple(fas)

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
