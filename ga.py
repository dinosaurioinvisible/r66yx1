
import numpy as np
from tqdm import tqdm
import evol_net
import robot_agent
import simplot

## TODO:
# clean!
# bounce with other robots or trees
# robot aren't moving!!

def ga(generations=100, population=100, t=100, m_rate=0.1):
    # lists to store genotypes and behaviour data
    genotypes = []
    genotypes_data = []
    # initial population
    # thresholds for the networks and parameters for robots
    ut = 0.5; lt = 0.1; vt = 0.9; weights = None
    # radius, ray length, fs angle, fs range
    r = 2.5; ray = 20; fs_a = 360; fs_r = 30
    initial_genotypes = [[ut, lt, vt, weights, r, ray, fs_a, fs_r] for n in range(population)]
    genotypes.append(initial_genotypes)
    # GA:
    for n_gen in range(generations):
        # go through all robots for one generation
        simrobots = simulate(genotypes[n_gen], t)
        # select (and sort) parents [fitness, robot] ...
        parents = select_parents(simrobots)
        # look at best individual
        print("fitness for best individual: {}".format(parents[0][0]))
        best_parameters = parents[0][1].genotype[4:]
        best_data = parents[0][1].data
        # for t in range(len(best_data)):
        #     print("\nt={}\n{}".format(t, best_data[t][]))
        simplot.runsim_plot([best_data], best_parameters)
        # check for break
        if len(genotypes) == generations:
            break
        # breed and replace
        new_genotypes = breeding(parents, m_rate)
        genotypes.append(new_genotypes)
    # return all genotypes and data
    return genotypes, genotypes_data

def simulate(genotypes, t):
    print("\n")
    # just try the genotypes, they don't change
    robots = []
    for rg in tqdm(range(len(genotypes))):
        # init robot
        robot = robot_agent.Robot(radius=genotypes[rg][4], ray_length=genotypes[rg][5], fs_angle=genotypes[rg][6], fs_range=genotypes[rg][7])
        # copy genome
        robot.net = evol_net.RNN(upper_t=genotypes[rg][0], lower_t=genotypes[rg][1], veto_t=genotypes[rg][2], weights=genotypes[rg][3])
        # trial
        tx = 0
        robot_data = []
        while tx < t:
            robot.act()
            tx += 1
        robots.append(robot)
    return robots

def select_parents(robots):
    print("\n")
    # check fitness and choose parents
    parents = []
    backup = []
    # for each robot
    for robot in robots:
        fitness = 0
        # for each timestep in simulation
        for t in range(len(robot.data)):
            # check for collisions
            if robot.data[t][4] == "collision":
                fitness -= 10
            # check for finding food
            if robot.data[t][4] == "tree":
                fitness += 5
        # decide
        if fitness > 0:
            # parents.append([fitness, robot.genotype, robot.data])
            parents.append([fitness, robot])
            print("robot {}, fitness = {}".format(len(backup), fitness))
        # backup.append([fitness, robot.genotype, robot.data])
        backup.append([1, robot])
    # if no robot has good fitness
    if len(parents) == 0:
        print("all died")
        parents = sorted(backup, reverse=True, key=lambda i:i[0])
        parents = parents[:10]
    # sort by fitness and return
    parents = sorted(parents, reverse=True, key=lambda i:i[0])
    print("\n{} robots from {} selected".format(len(parents), len(robots)))
    return parents

def breeding(parents, m_rate, max_pop=100):
    # parents: sorted [fitness, robot]...
    total_fitness = sum([parent[0] for parent in parents])
    parent_indexes = []
    fitness_counter = 0
    for parent in parents:
        fitness_counter += parent[0]
        parent_indexes.append(fitness_counter)
    # create population (starting with the parents)
    new_genotypes = [parent[1].genotype for parent in parents]
    print("\n{} parents to new generation".format(len(parents)))
    # add new individuals until 100
    while len(new_genotypes) < max_pop:
        # choose parent
        n = np.random.randint(total_fitness)
        for i in range(len(parent_indexes)):
            if n < parent_indexes[i]:
                # pg : parent genotype
                pg = parents[i][1].genotype
                # mutate and transmit
                ut = pg[0] + np.random.randint(-1,2)*m_rate
                lt = pg[1] + np.random.randint(-1,2)*m_rate
                vt = pg[2] + np.random.randint(-1,2)*m_rate
                wf = pg[3][0].flatten() + np.random.randint(-1,2)*m_rate
                vf = pg[3][1].flatten()
                for vij in range(len(vf)):
                    r = np.random.randint(100)
                    if r*m_rate < 100*m_rate:
                        vf[vij] = np.random.randint(2)
                w = wf.reshape(pg[3][0].shape)
                v = vf.reshape(pg[3][1].shape)
                weights = [w,v]
                # not touching this by now
                g4 = pg[4]
                g5 = pg[5]
                g6 = pg[6]
                g7 = pg[7]
                new_genotype = [ut, lt, vt, weights, g4, g5, g6, g7]
                new_genotypes.append(new_genotype)
                break
    print("{} new offsprings added".format(max_pop-len(parents)))
    return new_genotypes














#
