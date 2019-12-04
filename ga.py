
import numpy as np
from tqdm import tqdm
import evol_net
import robot_agent

# define genome variables
# create initial population
# population interactions
# select parents
# breed
# create mutated offspring
# evaluate new offspring
# replace members


def ga(generations=100, n_population=100, t=100):
    fulldata = []
    populations = []
    for n_gen in tqdm(range(generations)):
        # initial population
        if n_gen == 0:
            genomes = initial_population(n_population)
        else:
            genomes = populations[-1]
        # try the genomes
        new_genomes, simdata = robot_trials(genomes, t)
        # select parents
        parents = select_parents(simdata, new_genomes)
        # breed
        new_population = breeding(parents)
        populations.append(new_population)
        # save
        fulldata.append(simdata)
    return fulldata

def initial_population(population):
    ut = 0.5
    lt = 0.1
    weights = None
    genomes = [[ut, lt, weights] for n in range(population)]
    return genomes

def robot_trials(genomes, t):
    new_genomes = []
    simdata = []
    for genome in genomes:
        # init robot
        robot = robot_agent.Robot()
        # copy genome
        robot.net = evol_net.RNN(upper_t=genome[0], lower_t=genome[1], weights=genome[2])
        # trial
        tx = 0
        while tx < t:
            robot.act()
            tx += 1
            simdata.append(robot.data)
        new_genomes.append([robot.net.ut, robot.net.lt, robot.net.weights])
    return new_genomes, simdata

def select_parents(simdata, genomes):
    parents = []
    robot_index = 0
    for robot_data in simdata:
        fitness = 0
        min_energy = 0
        for t in range(len(robot_data)):
            # check for collisions
            if robot_data[t][4] == "collision":
                fitness -= 2
            # check for finding food
            if robot_data[t][4] == "tree":
                fitness += 5
            # check for historic min energy
            if robot_data[t][5] < min_energy:
                min_energy = robot_data[t][5]
        # decide
        if fitness >= 0 and min_energy>=0:
            parents.append([fitness, genomes[robot_index]])
            robot_index += 1
    # print("\n{} robots from {} selected".format(len(parents), len(genomes)))
    return parents

def breeding(parents):
    # parents [fitness, genomes]...
    # sort by fitness and breed random between 0 and fitness
    # parents = sorted(parents, reverse=True, key=lambda i:i[0])
    offs = [np.random.randint(0,p[0]+2) for p in parents]
    # new mutated population
    new_population = []
    for n in range(len(offs)):
        for n_off in range(n):
            #nh = parent[n][1][0] + np.random.randint(-1,2)
            ut = parents[n][1][0] + np.random.randint(-1,2)*0.1
            lt = parents[n][1][1] + np.random.randint(-1,2)*0.1
            weights = parents[n][1][2]
            new_genome = [ut, lt, weights]
            new_population.append(new_genome)
            if len(new_population) > 100:
                break
    return new_population



# def ga(generations=100, population=100, t=100):
#     simdata = []
#     genomes = []
#     print("\n")
#     # create initial population
#     for n in tqdm(range(population)):
#         # create robot
#         robot = robot_agent.Robot()
#         # define initial genome
#         robot.net = evol_net.RNN(upper_t=0.5, lower_t=0.1)
#         # robot.net = evol_net.RNN(n_hidden=5, upper_t=0.5, lower_t=0.1)
#         # individual trials
#         tx = 0
#         while tx < t:
#             robot.act()
#             tx += 1
#         simdata.append(robot.data)
#         # save genome
#         robot_genome = [robot.net.ut, robot.net.lt, robot.net.weights]
#         #robot_genome = [robot.net.n_hidden, robot.net.ut, robot.net.lt, robot.net.weights]
#         genomes.append(robot_genome)
#     # select parents
#     parents = []
#     robot_index = 0
#     for robot_data in simdata:
#         fitness = 0
#         min_energy = 0
#         for t in range(len(robot_data)):
#             # check for collisions
#             if robot_data[t][4] == "collision":
#                 fitness -= 1
#             # check for finding food
#             if robot_data[t][4] == "tree":
#                 fitness += 2
#             # check for historic min energy
#             if robot_data[t][5] < min_energy:
#                 min_energy = robot_data[t][5]
#         # decide
#         if fitness >= 0 and min_energy>=0:
#             parents.append([fitness, genomes[robot_index]])
#             robot_index += 1
#     print("\n{} robots from {} selected".format(len(parents), population))
#     # breed
#     # sort by fitness and breed random between 0 and fitness
#     parents = sorted(parents, reverse=True, key=lambda i:i[0])
#     offs = [np.random.randint(0,p[0]+1) for p in parents]
#     # new mutated population
#     new_population = []
#     for n in range(len(offs)):
#         for n_off in range(n):
#             #nh = parent[n][1][0] + np.random.randint(-1,2)
#             ut = parent[n][1][1] + np.random.randint(-1,2)*0.1
#             lt = parent[n][2][1] + np.random.randint(-1,2)*0.1
#             weights = parents[n][1][0]
#             new_genome = [ut, lt, weights]
#             new_population.append(new_genome)
#






#selex = ga()















#
