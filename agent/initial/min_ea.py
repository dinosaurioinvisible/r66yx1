
import numpy as np
import min_genotype
import min_trial
import _trial_animation
from copy import deepcopy
import pickle
import time
import sys
import os

class Evolve():
    def __init__(self, genotypes=None
        , n_gen=120
        , n_agents=35
        , n_trials=5
        , select_ratio=7
        , trial_t=1200
        , world_size=1000
        , n_trees=10
        , n_walls=4
        , mut_rate=0.11
        , anim=False
        , alarm=False
        , save=5):

        # trial
        self.n_gen = n_gen
        self.n_agents = n_agents
        self.n_trials = n_trials
        self.select_ratio = select_ratio
        self.trial_t = trial_t
        self.world_size = world_size
        self.n_trees = n_trees
        self.n_walls = n_walls
        self.breeding_dist = self.world_size/10
        self.mut_rate = mut_rate
        self.best_cases = []
        # genotypes
        self.genotypes = genotypes
        if not self.genotypes:
            self.genotypes = [min_genotype.Genotype() for i in range(self.n_agents)]
        elif len(self.genotypes) < self.n_agents:
            self.genotypes.extend([min_genotype.Genotype() for i in range(self.n_agents-len(genotypes))])
        # optional temp saves
        self.alarm = alarm
        self.save = save
        if self.save:
            dirname = "min_objs"
            self.dir_path = os.path.join(os.getcwd(),dirname)
            try:
                self.index = "{:04}".format(int(sorted([i for i in os.listdir(self.dir_path) if ".obj" in i])[-1].split("_")[1])+1)
            except:
                self.index = "0000"
            self.description = "{}v{}o{}e{}c".format(self.genotypes[0].vs_n,self.genotypes[0].olf_n,self.genotypes[0].e_n,self.genotypes[0].com_n)
            self.save_sim()
        # run
        self.simulation()


    def simulation(self):
        # for each generation
        for n in range(self.n_gen):
            # for each group
            ags_eval = []
            ags_ft_results = [[] for _ in range(self.n_agents)]
            for trial in range(self.n_trials):
                print("\ngeneration={}, trial={}".format(n, trial))
                # run trial
                xtrial = min_trial.Trial(t=self.trial_t, genotypes=self.genotypes, world=None, world_size=self.world_size, n_trees=self.n_trees, n_walls=self.n_walls)
                # results for every agent
                ft_agents = []
                for enum, agent in enumerate(xtrial.agents):
                    # compute distance to closest tree
                    ag_xn = agent.data.x[-1]
                    ag_yn = agent.data.y[-1]
                    min_dist = self.world_size
                    for tree in xtrial.world.trees:
                        dist = np.linalg.norm(np.array([ag_xn,ag_yn])-np.array([tree.x,tree.y]))
                        if dist < min_dist:
                            min_dist = dist
                    trial_cc = (self.world_size/self.n_trees-min_dist)/(self.world_size/self.n_trees)
                    # ax_tn = agent.data.x[-1]
                    # ay_tn = agent.data.y[-1]
                    # ax_t0 = agent.data.x[0]
                    # ay_t0 = agent.data.y[0]
                    # t0_dist = np.linalg.norm(np.array([tx,ty])-np.array([ax_t0,ay_t0]))
                    # tn_dist = np.linalg.norm(np.array([tx,ty])-np.array([ax_tn,ay_tn]))
                    # exp 1
                    # ft = final dist * ( 1 - ratio between initial and final dist )
                    # trial cc: best=1, same_dist=0, farther than d0=negative values
                    # exp 2
                    # trial_cc = (t0_dist-tn_dist)/t0_dist
                    # trial_ft = agent.e/1000 + trial_cc
                    # exp 3
                    # trial_ft = agent.e/1000
                    # exp 4
                    trial_ft = (agent.e/1000 + trial_cc)/2
                    ags_ft_results[enum].append(trial_ft)
                    # print("\nagent{}, trial_ft={}, agent.e={}, trial_cc={}, dist(t=0):{}, dist(t=n):{}".format(enum, round(trial_ft,2), round(agent.e,2), round(trial_cc,2), round(t0_dist,2),round(tn_dist,2)))
                    # print("\nagent{}, trial_ft={}, agent.e={}".format(enum, round(trial_ft,2), round(agent.e,2)))

            # evaluation function
            for enum, ag_results in enumerate(ags_ft_results):
                # best*1, ..., worst*n
                sorted_fts = sorted(ag_results, reverse=True)
                ft_sum = 0
                for i in range(self.n_trials):
                    ft_sum += (i+1) * sorted_fts[i]
                agent_ft = 2/self.n_trials*(self.n_trials+1) * ft_sum
                ags_eval.append([self.genotypes[enum], agent_ft])
            # sort, print, save
            best_agents = sorted(ags_eval, key=lambda x:x[1], reverse=True)[:self.select_ratio]
            print("\ngeneration {} best agents:".format(n))
            for enum,agent in enumerate(best_agents):
                print("agent {} energy: {}".format(enum, round(agent[1],2)))
            print("")
            self.best_cases.append(best_agents)
            if len(self.best_cases)%self.save == 0:
                self.save_sim()

            # new generation genotypes
            self.genotypes = []
            # best genotype replication (egoistical)
            self.genotypes.append(deepcopy(best_agents[0][0]))
            # breeding and mutations
            breeds = 0; muts = 0
            # parents
            parents = [pa for pa in best_agents if pa[1] > 0]
            # in case there is no agents with fitness above 0 (early gens)
            if len(parents)==0:
                while len(self.genotypes) < self.n_agents:
                    self.mutate(self.genotypes[0])
                    muts += 1
            # crossovers
            total_ft = sum([pa[1] for pa in parents])
            while len(self.genotypes) < self.n_agents:
                ix = np.random.uniform(0,total_ft)
                index_px = int(ix/total_ft*len(parents))
                iy = np.random.uniform(0,total_ft)
                index_py = int(iy/total_ft*len(parents))
                px = parents[index_px][0]
                py = parents[index_py][0]
                self.breed(px,py)
                if px==py:
                    muts += 1
                else:
                    breeds += 1
                # prints
                sys.stdout.write("\r1 replication, {} breedings and {} self-mutations".format(breeds,muts))
                sys.stdout.flush()
                time.sleep(0.2)
            print("")
        # save, alarm and end
        self.save_sim(filename="evolexp")
        if self.alarm:
            try:
                os.system("osascript -e \"set Volume 5\" ")
                os.system("open -a vlc ~/desktop/brigth-engelberts-free-me-now.mp3")
            except:
                pass


    def breed(self, px, py):
        # new weights shape
        parents = [px,py]
        network = []
        # check number of hidden units
        xn_net = px.n_input+px.n_hidden+px.n_output
        yn_net = py.n_input+py.n_hidden+py.n_output
        # mix networks
        if xn_net == yn_net:
            for ni in range(xn_net):
                pn = np.random.choice([0,1])
                nx = parents[pn].network[ni]
                network.append(nx)
        else:
            pn = np.random.choice([0,1])
            network = parents[pn].network
        # sensors
        pn = np.random.choice([0,1])
        vrg = parents[pn].vs_theta
        vth = parents[pn].vs_theta
        pn = np.random.choice([0,1])
        org = parents[pn].olf_range
        oth = parents[pn].olf_theta
        new_genotype = min_genotype.Genotype(network=network, vs_range=vrg, vs_theta=vth, olf_range=org, olf_theta=oth)
        # mutate the crossover
        self.mutate(new_genotype)

    def mutate(self, px):
        # mutate weights and thresholds
        for nx in px.network:
            for i in range(len(nx.wx)):
                # eliminate
                if np.random.uniform(0,1)<self.mut_rate/3:
                    nx.wx[i] = 0
                # reset
                if np.random.uniform(0,1)<self.mut_rate/3:
                    nx.wx[i] = np.random.uniform(-0.5,1)
                # change weight
                if np.random.uniform(0,1)<self.mut_rate:
                    nx.wx[i] += np.random.uniform(-0.1,0.1)
            # thresholds
            if np.random.uniform(0,1)<self.mut_rate:
                nx.lt += np.random.uniform(-0.05,0.05)
            if np.random.uniform(0,1)<self.mut_rate:
                nx.ut += np.random.uniform(-0.05,0.05)
            # check thresholds
            nx.wx = np.where(nx.wx<-1,-1, np.where(nx.wx>1,1, nx.wx))
            nx.lt = np.where(nx.lt>-0.5,-0.5, np.where(nx.lt<-1,-1, nx.lt))
            nx.ut = np.where(nx.ut<0.5,0.5, np.where(nx.ut>1, 1, nx.ut))
        # hidden units number
        # nhu = px.n_hidden
        # if np.random.uniform(0,1)<self.mut_rate:
        #     nhu += np.random.choice([-1,1])
        # nhu = 2 if nhu < 2 else nhu
        # nhu = 5 if nhu > 5 else nhu
        # if nhu < px.n_hidden:
        #     # index
        #     nx_del = np.random.randint(px.n_input,px.n_input+px.n_hidden)
        #     # delete from every neuron wx
        #     for nx in px.network:
        #         nx.wx = np.delete(nx.wx, nx_del)
        #     # delete neuron
        #     del(px.network[nx_del])
        #     px.n_hidden -= 1
        # elif nhu > px.n_hidden:
        #     # index
        #     nx_add = np.random.randint(px.n_input,px.n_input+px.n_hidden)
        #     # adjust wx for each neuron
        #     for nx in px.network:
        #         w = np.random.uniform(-1,1)
        #         nx.wx = np.insert(nx.wx, nx_add, w)
        #     # adjust n hidden and append new neuron
        #     px.n_hidden += 1
        #     from min_net import Neuron
        #     nx = Neuron()
        #     nx.wx = np.concatenate((np.zeros(px.n_input),np.random.uniform(-1,1,size=(px.n_hidden+px.n_output))))
        #     px.network.insert(nx_add,nx)
        # sensors
        # vis vs olf (ranges)
        vs_range = px.vs_range
        olf_range = px.olf_range
        if np.random.uniform(0,1)<self.mut_rate:
            di = np.random.randint(-2,3)
            vs_range += di
            olf_range -= di
        # sensors parameters: vision
        # vision sensors location
        # vision range and theta
        vs_theta = px.vs_theta
        if np.random.uniform(0,1)<self.mut_rate:
            dv = np.random.randint(-2,3)
            vs_range += dv
            vs_theta -= dv
        # sensors parameters: olf
        # olf sensors location
        # olf range and theta
        olf_theta = px.olf_theta
        if np.random.uniform(0,1)<self.mut_rate:
            do = np.random.randint(-2,3)
            olf_range += do
            olf_theta -= do
        # check ranges
        vs_range = px.vs_range if vs_range<5 or vs_range>55 else vs_range
        vs_theta = px.vs_theta if vs_theta<10 or vs_theta>((360/px.vs_n)*2/3) else vs_theta
        olf_range = px.olf_range if olf_range<5 or olf_range>55 else olf_range
        olf_theta = px.olf_theta if olf_theta<10 or olf_theta>350 else olf_theta
        # make new genotype and return
        new_genotype = min_genotype.Genotype(vs_range=vs_range, vs_theta=vs_theta, olf_range=olf_range, olf_theta=olf_theta, network=px.network)
        self.genotypes.append(new_genotype)


    def save_sim(self, filename="temp"):
        # filename and path
        i_filename = "{}_{}_{}_ags={}_t={}_gen={:03}.obj".format(filename,self.index,self.description,self.n_agents,self.trial_t,len(self.best_cases))
        if not os.path.isdir(self.dir_path):
            os.mkdir(self.dir_path)
        i_path = os.path.join(self.dir_path,i_filename)
        # look for previous temps
        temps = sorted([i for i in os.listdir(self.dir_path) if self.index in i])
        # check if file already exists
        if os.path.isfile(i_path):
            print("file already exists at {}".format(i_path))
            import time
            i_filename += "_{}".format(time.ctime())
            i_path = os.path.join(self.dir_path,i_filename)
        # save with pickle
        with open(i_path, "wb") as exp_file:
            pickle.dump(self.best_cases, exp_file)
        print("\n{} object saved at: \n{}\n".format(i_filename, i_path))
        # remove previous versions if finished (except last one, just in case)
        if filename != "temp" or len(temps)>5:
            for tempfile in temps[:-1]:
                os.remove(os.path.join(self.dir_path,tempfile))
                print("removed temporal file: {}".format(tempfile))
            print("")



#Evolve()














    #
