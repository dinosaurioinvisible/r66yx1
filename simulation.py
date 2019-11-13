
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
        print("\ntime step: {}/{}".format(tx+1,t))
        simrobot.act()
        tx += 1
    # return data
    return simrobot.data

simdata = runsim()

def runsim_plot(data):

    simlocations = [i[0] for i in data]

    fig, ax = plt.subplots()
    xdata, ydata = [], []
    locations, = plt.plot([], [], "ro")

    def init():
        ax.set_xlim(0, world.xmax)
        ax.set_ylim(0, world.ymax)
        for wall in world.walls[4:]:
            ax.plot([wall[0][0],wall[1][0]], [wall[0][1],wall[1][1]])
        return locations,

    def update(frame):
        xdata.append(frame[0])
        ydata.append(frame[1])
        locations.set_data(xdata, ydata)
        return locations,

    ani = animation.FuncAnimation(fig, update, frames=simlocations, init_func=init, blit=True)
    plt.show()

runsim_plot(simdata)


#if __name__ == "__main__":
#    main()
