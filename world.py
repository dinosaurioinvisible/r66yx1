
import numpy as np

# variables
xmax = 100
ymax = 100
n_walls = 5
walls_loc = "random"

def allocate_walls(xmax, ymax, n_walls, walls_loc):
    walls = []
    # borders
    walls.append([[0,0],[xmax,0]])
    walls.append([[0,0],[0,ymax]])
    walls.append([[0,ymax],[xmax,ymax]])
    walls.append([[xmax,0],[xmax,ymax]])
    # other optional walls
    if  n_walls>4 and walls_loc == "random":
        for n in range(n_walls-4):
            ax = np.random.randint(10,90)
            ay = np.random.randint(10,90)
            bx = np.random.randint(10,90)
            by = np.random.randint(10,90)
            walls.append([[ax,ay],[bx,by]])
    elif walls_loc>4 and walls_loc != "random":
        for n in range(n_walls-4):
            ax = input("ax for wall {}: ".format(n+4))
            ay = input("ay for wall {}: ".format(n+4))
            bx = input("bx for wall {}: ".format(n+4))
            by = input("by for wall {}: ".format(n+4))
            walls.append([[ax,ay],[bx,by]])
    print("\nwalls alocated at:")
    for wall in walls:
        print("A:{} to B:{}".format(wall[0],wall[1]))
    return walls

walls = allocate_walls(xmax, ymax, n_walls, walls_loc)
