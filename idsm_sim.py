
import idsm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec


def idsm_simulation(tx=0, dt=0.1, t=65, map=False):
    simdata = []
    robot = idsm.Agent(dt)
    loc = np.array([-2.5])
    sx = 0
    # training
    while tx < 20:
        sx = 1/(1+loc**2)
        mx = np.array([np.cos(tx/2)/2])
        robot.train(sx, mx)
        loc += mx*dt
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        # print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))

    # mapping of motor influence
    influence_data = []
    if map:
        for motor in np.arange(0.02,0.98,0.02):
            for sensor in np.arange(0.02,0.98,0.02):
                sm = np.array([motor, sensor])
                mu = robot.motor_fx(sm)
                xt = np.sqrt((1/sensor)-1)
                nmotor = motor + mu[0]*0.1
                xt = xt + 0.1 * (nmotor+1)/2
                nsensor = 1/(1+xt**2)
                influence_data.append([sensor,motor,nsensor-sensor,nmotor-motor])
                # print("sensor:{}, motor:{}, nsen-sen:{}, nmotor-motor:{}".format(sensor,motor,nsensor-sensor,nmotor-motor))
    # idsm
    while tx < t:
        sx = 1/(1+loc**2)
        mx = robot.idsm(sx)
        loc += ((mx*2)-1)*dt
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        # print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))
        # import pdb; pdb.set_trace()
    # idsm rellocated
    loc = np.array([-2.5])
    while tx < t:
        sx = 1/(1+loc**2)
        mx = robot.idsm(sx)
        loc += ((mx*2)-1)*dt
        tx += dt
        simdata.append(np.concatenate((sx,loc)))
        #print("tx:{} - sx:{} - mx:{}, loc:{}".format(tx,sx,mx,loc))
    simdata_reduced = [simdata[sn] for sn in range(len(simdata)) if sn%10==0]
    return simdata_reduced, influence_data


def idsm_streamplot(influence_data):
    if len(influence_data) == 0:
        return None
    Y,X = np.mgrid[0.02:0.98:48j, 0.02:0.98:48j]
    U,V = np.mgrid[0.0:0.0:48j, 0.0:0.0:48j]
    # import pdb; pdb.set_trace()
    for n in range(len(influence_data)):
        for y in range(48):
            U[n%48][y], V[n%48][y] = influence_data[n][2], influence_data[n][3]
    speed = np.sqrt(U*U+V*V)
    # import pdb; pdb.set_trace()
    fig = plt.figure(figsize=(5,5))
    gs = gridspec.GridSpec(nrows=1,ncols=1,height_ratios=[1])
    # vary linewidth
    ax2 = fig.add_subplot(gs[0,0])
    lw = speed/speed.max()
    ax2.streamplot(X,Y,U,V, density=0.7, color="k", linewidth=lw)
    ax2.set_title("motor_influence")
    plt.tight_layout()
    plt.show()


def idsm_animation(simdata):
    robot_sensors = [data[0] for data in simdata]
    robot_locs = [data[1] for data in simdata]
    fig = plt.figure()
    ax = plt.axes(xlim=(0,len(simdata)), ylim=(min(robot_locs),max(robot_locs)))
    robot = plt.Circle((0, robot_locs[0]), radius=0.1, color="blue", fill=True)
    xlocs, ylocs = [], []
    past_locations, = plt.plot([], [], color="grey")

    def init():
        xi = [0, 20, 35, len(robot_locs)]
        yi = [robot_locs[0], robot_locs[20], robot_locs[35], robot_locs[-1]]
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



idsm_data, influence_data = idsm_simulation()
idsm_streamplot(influence_data)
idsm_animation(idsm_data)

































































#
