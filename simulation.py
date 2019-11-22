
import geometry
import world
import robot_agent
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#TODO
# after collisions
# urgency fx, to define speed
# parameter/variable to differentiate lw and rw speed
# parameter/variable to alter irval
# compute for all ray_spread values (5 in the original)
# innner wall could rotate clockwise
# ir input should see obstacles and food (classify)?
# connect ir values to motor behaviour
# ir input -> net -> output motor


def runsim(t=100, n_robots=5):
    tx = 0
    simrobots = [robot_agent.Robot() for n in range(n_robots)]
    while tx < t:
        for simrobot in simrobots:
            simrobot.act()
        tx += 1
    data = [simrobot.data for simrobot in simrobots]
    return data

def runsim_plot(data, past=True):
    # definitions
    fig = plt.figure()
    ax = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    # organize data
    simlocations = []
    orientations = []
    sensors_data = []
    ir_vals = []
    for t in range(len(data[0])):
        simlocations.append([simrobot[t][0] for simrobot in data])
        orientations.append([simrobot[t][1] for simrobot in data])
        sensors_data.append([simrobot[t][2] for simrobot in data])
        ir_vals.append([simrobot[t][3] for simrobot in data])
    # plot basics for robots
    robots = []
    robot = plt.Circle(0,0)
    n_robots = len(data)
    for i in range(n_robots):
        robot_obj = plt.Circle((0,0), radius=world.xmax/100, fill=False)
        robots.append(robot_obj)
    # past locations
    xlocs, ylocs = [], []
    past_locations, = plt.plot([], [], color="grey")
    # sensors
    rays = []
    ray, = plt.plot([], [])
    n_sensors = len(sensors_data[0][0])
    for i in range(n_robots+n_sensors*n_robots):
        # main orientations + sensors for each robot[1:]
        scolor = "black" if i < n_robots else "orange"
        ray_obj = ax.plot([],[], color=scolor)[0]
        rays.append(ray_obj)

    def init():
        # other walls
        walls, trees = world.walls, world.trees
        for wall in world.walls[4:]:
            ax.plot([wall[0][0],wall[1][0]], [wall[0][1],wall[1][1]], color="black")
        # trees
        trees_x, trees_y = zip(*world.trees)
        ax.scatter(trees_x,trees_y, color="green")
        # starting point
        xi = [robot_loc[0] for robot_loc in simlocations[0]]
        yi = [robot_loc[1] for robot_loc in simlocations[0]]
        ax.scatter(xi, yi, color="grey")
        # add circles
        for robot in robots:
            ax.add_patch(robot)
        return robot,

    def animate(i):
        # current location
        x = [robot_loc[0] for robot_loc in simlocations[i]]
        y = [robot_loc[1] for robot_loc in simlocations[i]]
        o = [np.radians(robot_or) for robot_or in orientations[i]]
        # allocate robot
        for enum, robot in enumerate(robots):
            #import pdb; pdb.set_trace()
            robot.center = (x[enum],y[enum])
        # past locations
        xlocs.append(x)
        ylocs.append(y)
        # more than one you can't see anything
        if past == True and len(xlocs) < len(simlocations):
            past_locations.set_data(xlocs, ylocs)
        # sensors list, added proyection for main orientation
        sx = [[x[n], x[n]+10*np.cos(o[n])] for n in range(len(x))]
        sy = [[y[n], y[n]+10*np.sin(o[n])] for n in range(len(y))]
        # ir beams proyections
        for robot_i in range(n_robots):
            for ir_sensor in sensors_data[i][robot_i]:
                # data for each sensor for each robot
                spos, so, sray, sleft, sright = ir_sensor
                rs_x, rs_y = spos
                # center ray of beam
                re_x = rs_x + sray*np.cos(so)
                re_y = rs_y + sray*np.sin(so)
                # left most ray from left most beam
                re_xl = rs_x + sray*np.cos(sleft)
                re_yl = rs_y + sray*np.sin(sleft)
                # right most ray from right most beam
                re_xr = rs_x + sray*np.cos(sright)
                re_yr = rs_y + sray*np.sin(sright)
                # ir_rays
                sx.append([rs_x, re_xl, re_x, re_xr, rs_x])
                sy.append([rs_y, re_yl, re_y, re_yr, rs_y])
        # plot ir_rays
        for enum, ray in enumerate(rays):
            ray.set_data(sx[enum], sy[enum])

        # import pdb; pdb.set_trace()
        return (past_locations,)+tuple(robots)+tuple(rays)

    anim = animation.FuncAnimation(fig, animate,
                                    init_func=init,
                                    frames=100,
                                    blit=True)
    plt.show()


# run
simdata = runsim()
print("\ndata:")
for dataline in range(len(simdata[0])):
    print("\nt={}".format(dataline))
    for simrobot in simdata:
        print(simrobot[dataline])
runsim_plot(simdata)


#if __name__ == "__main__":
#    main()
