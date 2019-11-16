
import geometry
import world
import robot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pdb

def runsim(t=100):
    simrobot=robot.Robot()
    #print(simrobot)
    tx = 0
    data = []
    while tx < t:
        #print("\ntime step: {}/{}".format(tx+1,t))
        simrobot.act()
        tx += 1
    # return data
    return simrobot.data

def runsim_plot(data):
    # definitions
    simlocations = [i[0] for i in data]
    fig, ax = plt.subplots()
    xdata, ydata = [], []
    locations, = plt.plot([], [], "ro")
    past_locations, = plt.plot([], [], color="grey")

    def init():
        # draw the fixed elements and init
        # boundary walls
        walls, trees = world.walls, world.trees
        ax.set_xlim(0, world.xmax)
        ax.set_ylim(0, world.ymax)
        # other walls
        for wall in world.walls[4:]:
            ax.plot([wall[0][0],wall[1][0]], [wall[0][1],wall[1][1]], color="black")
        # trees
        trees_x, trees_y = zip(*world.trees)
        ax.scatter(trees_x,trees_y, color="blue")
        # starting point
        xi = simlocations[0][0]
        yi = simlocations[0][1]
        ax.scatter(xi, yi, color="grey")
        return locations,

    def update(frame):
        # xdata = frame[0]
        # ydata = frame[1]
        # locations.set_data(xdata, ydata)
        xdata.append(frame[0])
        ydata.append(frame[1])
        if len(xdata) <= len(simlocations):
            past_locations.set_data(xdata, ydata)
        locations.set_data(xdata[-1], ydata[-1])
        return locations, past_locations

    ani = animation.FuncAnimation(fig, update, frames=simlocations, init_func=init, blit=True)
    plt.show()

# run
simdata = runsim()
print("\ndata:")
[print(dataline) for dataline in simdata]
runsim_plot(simdata)


#if __name__ == "__main__":
#    main()
