
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon


def sim_animation(t, world, agents):
    # def
    fig = plt.figure()
    ax = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    ax.grid = True
    time = ax.text(world.xmax/2, world.ymax+10,str("time: 0"),ha="left",va="top")
    anim_running = True
    # plot basics for agents
    ags = []; olfs = []; coms = []; irs = []; feeds = []
    for agent in agents:
        ag, = plt.plot([],[], color="black")
        ags.append(ag)
        ir1, = plt.plot([],[], color="orange")
        ir2, = plt.plot([],[], color="orange")
        irs.append([ir1, ir2])
        olf, = plt.plot([],[], color="yellow")
        olfs.append(olf)
        com, = plt.plot([],[], color="blue")
        coms.append(com)
        feed, = plt.plot([],[], color="grey")
        feeds.append(feed)

    # to pause the animation
    def onClick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True

    def init():
        # optional walls, trees and initial locations
        for wall in world.walls[4:]:
            ax.plot([wall.xmin, wall.xmax], [wall.ymin, wall.ymax], color="black")
        for tree in world.trees:
            # ax.plot(*tree.area.exterior.xy, color="green")
            tx = plt.Circle((tree.x, tree.y), radius=tree.r, color="green", fill=True)
            ax.add_patch(tx)
        return True

    def animate(i):
        time.set_text("time: "+str(i))
        # for each agent
        for enum, ag in enumerate(ags):
            x = agents[enum].data.x[i]
            y = agents[enum].data.y[i]
            o = agents[enum].data.o[i]
            e = agents[enum].data.e[i]
            print("\nt: {}".format(i))
            print("x,y: {},{}".format(x,y))
            print("o: {} > {}".format(o, np.degrees(o)))
            print("energy: {}".format(e))
            ag.set_data(*agents[enum].data.area[i].exterior.xy)
            # ir sensors
            for n in range(len(irs[enum])):
                irs[enum][n].set_data(*agents[enum].data.vs_sensors[i][n].exterior.xy)
                vx = True if agents[enum].data.env_info[i][n] != 0 else False
                irs[enum][n].set_visible(vx)
            all_irs = [ir for irx in irs for ir in irx]
            # olf sensor
            olfs[enum].set_data(*agents[enum].data.olf_sensor[i].exterior.xy)
            vx = True if agents[enum].data.env_info[i][-1] != 0 else False
            olfs[enum].set_visible(vx)
            # feeding info
            feeds[enum].set_data(*agents[enum].data.feeding_area[i].exterior.xy)

            # communication info
            coms[enum].set_data(*agents[enum].data.com_area[i].exterior.xy)

        return time, tuple(ags)+tuple(all_irs)+tuple(olfs)+tuple(coms)+tuple(feeds)
        #return time, tuple(ags)+tuple(irs)+tuple(olfs)+tuple(coms)+tuple(feeds)

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate,
                                        init_func=init,
                                        frames=t,
                                        interval=200,
                                        blit=False)
    plt.show()




import _trial
trial = _trial.Trial()
x = trial.trial()
sim_animation(x[0],x[1],x[2])
























#
