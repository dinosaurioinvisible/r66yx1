
import numpy as np
from tqdm import tqdm
import evol_net
import robot_agent
import simplot

## TODO:
# clean!
# bounce with other robots or trees
# robot aren't moving!!

def ga(generations=100, population=100, t=100, m_rate=0.5):
    # lists to store genotypes and behaviour data
    genotypes = []
    genotypes_data = []
    # initial population
    # radius, ray length, fs angle, fs range
    r = 2.5; ray=20; fs_a=360; fs_r=30
    # thresholds for the networks and parameters for robots
    n_in=3; n_hidden=2; n_out=4; ut=0.5; lt=0.1; vt=0.9; W=[]; V=[]
    initial_genotypes = [[r, ray, fs_a, fs_r, n_in, n_out, n_hidden, ut, lt, vt, W, V] for n in range(population)]
    genotypes.append(initial_genotypes)
    # GA:
    for n_gen in range(generations):
        # go through all robots for one generation
        simrobots = simulate(genotypes[n_gen], t)
        # select (and sort) parents [fitness, robot] ...
        parents = select_parents(simrobots)
        # look at best individual
        print("fitness for best individual: {}".format(parents[0][0]))
        best_robot = parents[0][1]
        best_parameters = best_robot.genotype[:4]
        best_data = best_robot.data
        # print best robot matrices
        W = best_robot.net.W
        V = best_robot.net.V
        print(W)
        print(V)
        # animate best robot
        simplot.runsim_plot([best_data], best_parameters)
        # check for break
        if len(genotypes) == generations:
            break
        # breed and replace
        new_genotypes = breeding(parents, m_rate, population)
        genotypes.append(new_genotypes)
        # import pdb; pdb.set_trace()
    # return all genotypes and data
    return genotypes, genotypes_data

def simulate(genotypes, t):
    print("\n")
    # just try the genotypes, they don't change
    robots = []
    for rg in tqdm(range(len(genotypes))):
        # copy genome and init robot
        robot = robot_agent.Robot(radius=genotypes[rg][0], ray_length=genotypes[rg][1], fs_angle=genotypes[rg][2], fs_range=genotypes[rg][3], n_in=genotypes[rg][4], n_hidden=genotypes[rg][5], n_out=genotypes[rg][6], upper_t=genotypes[rg][7], lower_t=genotypes[rg][8], veto_t=genotypes[rg][9], W=genotypes[rg][10], V=genotypes[rg][11])
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
            # print("robot {}, fitness = {}".format(len(backup), fitness))
        # backup.append([fitness, robot.genotype, robot.data])
        backup.append([1, robot])
    # if no robot has good fitness
    if len(parents) == 0:
        print("all died")
        parents = sorted(backup, reverse=True, key=lambda i:i[0])
        parents = parents[:10]
    # sort by fitness and return
    parents = sorted(parents, reverse=True, key=lambda i:i[0])
    print("\n{} robots from {} survived".format(len(parents), len(robots)))
    return parents

def breeding(parents, m_rate, max_pop=100):
    # delete 1/4 if everyone survived
    if len(parents) == 100:
        del(parents[75:])
    # parents: sorted [fitness, robot]...
    total_fitness = sum([parent[0] for parent in parents])
    parent_indexes = []
    fitness_counter = 0
    for parent in parents:
        fitness_counter += parent[0]
        parent_indexes.append(fitness_counter)
    # create population (starting with the parents)
    # new_genotypes = [parent[1].genotype for parent in parents]
    new_genotypes = []
    print("\n{} parents to new generation".format(len(parents)))
    # add new individuals until 100
    while len(new_genotypes) < max_pop:
        # choose parent
        index = None
        n = np.random.randint(total_fitness)
        for i in range(len(parent_indexes)):
            if n < parent_indexes[i]:
                index = i
        # pg : parent genotype
        pg = parents[index][1].genotype
        # mutate and transmit
        ut = pg[7] + np.random.randint(-1,2)*m_rate
        lt = pg[8] + np.random.randint(-1,2)*m_rate
        vt = pg[9] + np.random.randint(-1,2)*m_rate
        # mutate weights
        wf = pg[10].flatten()
        vf = pg[11].flatten()
        wfx = np.array([wij+np.random.randn() if np.random.randint(100)<100*m_rate else wij for wij in wf])
        vfx = np.array([np.random.randint(2) if np.random.randint(100)<100*m_rate else vij for vij in vf])
        W = wfx.reshape(pg[10].shape)
        V = vfx.reshape(pg[11].shape)
        # not touching this for now
        g0 = pg[0]
        g1 = pg[1]
        g2 = pg[2]
        g3 = pg[3]
        g4 = pg[4]
        g5 = pg[5]
        g6 = pg[6]
        # muted genotype
        new_genotype = [g0, g1, g2, g3, g4, g5, g6, ut, lt, vt, W, V]
        new_genotypes.append(new_genotype)
    print("{} new offsprings added".format(max_pop-len(parents)))
    return new_genotypes














#
