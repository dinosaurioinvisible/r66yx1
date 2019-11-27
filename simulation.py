
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
# anticipate collisions -> RNN
# connect ir values to motor behaviour
# toto > 1. reactive rules > 2. landmarks > 3. distributed map of environment
# fixation of reacting rules as patterns (habits)
# ir input -> net -> output motor
# subsumption: avoid > wander > explore
# avoid robot-robot collisions

def runsim(t=100, n_robots=1):
    tx = 0
    simrobots = [robot_agent.Robot() for n in range(n_robots)]
    while tx < t:
        for simrobot in simrobots:
            simrobot.act()
        tx += 1
    data = [simrobot.data for simrobot in simrobots]
    parameters = simrobot.parameters
    return data, parameters

def runsim_plot(data, parameters, past=False, start=False):
    # definitions
    fig = plt.figure()
    ax = plt.axes(xlim=(0,world.xmax), ylim=(0,world.ymax), aspect="equal")
    # parameters
    robot_radius = parameters[0]
    ir_range = parameters[1]
    fs_range = parameters[2]
    # organize data
    simlocations = []
    orientations = []
    ir_data = []
    fs_vals = []
    for t in range(len(data[0])):
        simlocations.append([simrobot[t][0] for simrobot in data])
        orientations.append([simrobot[t][1] for simrobot in data])
        ir_data.append([simrobot[t][2] for simrobot in data])
        fs_vals.append([simrobot[t][3] for simrobot in data])
    # plot basics for robots
    robots = []
    robot = plt.Circle(0,0)
    fsensors = []
    fsensor = plt.Circle(0,0)
    n_robots = len(data)
    for i in range(n_robots):
        robot_obj = plt.Circle((0,0), radius=robot_radius, color="blue", fill=True)
        robots.append(robot_obj)
        fsensor_obj = plt.Circle((0,0), radius=fs_range, color="blue", fill=False, ls="dashed")
        fsensors.append(fsensor_obj)
    # past locations
    xlocs, ylocs = [], []
    past_locations, = plt.plot([], [], color="grey")
    # sensors
    rays = []
    ray, = plt.plot([], [])
    n_sensors = len(ir_data[0][0])
    for i in range(n_robots+2*n_sensors*n_robots):
        # main orientations + left/right rays for each sensor for each robot
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
        if start == True and n_robots == 1:
            xi = [robot_loc[0] for robot_loc in simlocations[0]]
            yi = [robot_loc[1] for robot_loc in simlocations[0]]
            ax.scatter(xi, yi, color="grey")
        # add circles
        for robot in robots:
            ax.add_patch(robot)
        for fsensor in fsensors:
            ax.add_patch(fsensor)
        return robot, fsensor,

    def animate(i):
        # current robots locations
        x = [robot_loc[0] for robot_loc in simlocations[i]]
        y = [robot_loc[1] for robot_loc in simlocations[i]]
        o = [np.radians(robot_or) for robot_or in orientations[i]]
        # allocate robot
        for enum, robot in enumerate(robots):
            robot.center = (x[enum], y[enum])
        # current food sensors locations
        for enum, fsensor in enumerate(fsensors):
            fsensor.center = (x[enum], y[enum])
            if fs_vals[i][0] != None:
                fsensor.set_color("red")
            else:
                fsensor.set_color("blue")
        # past locations
        xlocs.append(x)
        ylocs.append(y)
        # more than one you can't see anything
        if past == True and n_robots == 1:
            past_locations.set_data(xlocs, ylocs)
        # sensors list, added proyection for main orientation
        sx = [[x[n], x[n]+10*np.cos(o[n])] for n in range(len(x))]
        sy = [[y[n], y[n]+10*np.sin(o[n])] for n in range(len(y))]
        irs = [None]
        # ir beams proyections
        for robot_i in range(n_robots):
            for ir_sensor in ir_data[i][robot_i]:
                # data for each sensor for each robot
                rs_x, rs_y = ir_sensor[0]
                so = np.radians(ir_sensor[1])
                sleft = np.radians(ir_sensor[2])
                sright = np.radians(ir_sensor[3])
                ir_val = ir_sensor[4]
                # center ray of beam
                re_x = rs_x + ir_range*np.cos(so)
                re_y = rs_y + ir_range*np.sin(so)
                # left most ray from left most beam
                re_xl = rs_x + ir_range*np.cos(sleft)
                re_yl = rs_y + ir_range*np.sin(sleft)
                # right most ray from right most beam
                re_xr = rs_x + ir_range*np.cos(sright)
                re_yr = rs_y + ir_range*np.sin(sright)
                # ir_rays
                sx.append([rs_x, re_xl])
                sy.append([rs_y, re_yl])
                sx.append([rs_x, re_xr])
                sy.append([rs_y, re_yr])
                # ir value for sensor
                irs.extend([ir_val, ir_val])
        # plot ir_rays
        for enum, ray in enumerate(rays):
            ray.set_data(sx[enum], sy[enum])
            if irs[enum]:
                ray.set_color("orange")
            else:
                ray.set_color("black")

        # import pdb; pdb.set_trace()
        return (past_locations,)+tuple(robots)+tuple(rays)+tuple(fsensors)

    anim = animation.FuncAnimation(fig, animate,
                                    init_func=init,
                                    frames=100,
                                    blit=True)
    plt.show()


# run
simdata, simparams = runsim()
print("\ndata:")
for dataline in range(len(simdata[0])):
    print("\nt={}".format(dataline))
    for simrobot in simdata:
        print(simrobot[dataline])
runsim_plot(simdata, simparams)


#if __name__ == "__main__":
#    main()
