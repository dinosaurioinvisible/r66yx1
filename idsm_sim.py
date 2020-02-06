
import idsm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def idsm_simulation(tx=0, dt=0.1, t=75):
    simdata = []
    robot = idsm.Agent(dt)
    loc = np.array([-2.5])
    # training
    while tx < 20:
        mx = np.array([np.cos(tx/2)/2])
        sx = 1/(1+loc**2)
        robot.train(sx, mx)
        loc += mx*dt
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        #print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))
    # idsm
    while tx < 35:
        mx = robot.idsm(sx)
        sx = 1/(1+loc**2)
        loc += mx*dt
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        #print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))
    # idsm rellocated
    loc = np.array([-2.5])
    while tx < t:
        mx = robot.idsm(sx)
        sx = 1/(1+loc**2)
        loc += mx
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        #print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))
    simdata_reduced = [simdata[sn] for sn in range(len(simdata)) if sn%10==0]
    return simdata_reduced



def idsm_animation(simdata):
    fig = plt.figure()
    ax = plt.axes(xlim=(0,len(simdata)), ylim=(-5,0))
    robot_sensors = [data[0] for data in simdata]
    robot_locs = [data[1] for data in simdata]
    robot = plt.Circle((0, robot_locs[0]), radius=0.1, color="blue", fill=True)
    xlocs, ylocs = [], []
    past_locations, = plt.plot([], [], color="grey")

    def init():
        xi = [0, 20, 35]
        yi = [robot_locs[0], robot_locs[19], robot_locs[0]]
        ax.scatter(xi, yi, color="grey")
        ax.add_patch(robot)
        return robot,

    def animate(i):
        x = i
        y = robot_locs[i]
        robot.center = (x,y)
        xlocs.append(x)
        ylocs.append(y)
        past_locations.set_data(xlocs, ylocs)
        return robot, past_locations

    anim = animation.FuncAnimation(fig, animate,
                                    init_func=init,
                                    frames=len(simdata),
                                    blit=True)
    plt.show()



idsm_data = idsm_simulation()
idsm_animation(idsm_data)




































































#
