
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
        , n_trials=10
        , select_ratio=7
        , trial_t=1500
        , world_size=1000
        , n_trees=10
        , n_walls=4
        , mut_rate=0.1
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
                # fitness according to change in distance
                tx = xtrial.world.trees[0].x
                ty = xtrial.world.trees[0].y
                # results for every agent
                ft_agents = []
                for enum, agent in enumerate(xtrial.agents):
                    ax_t0 = agent.data.x[0]
                    ay_t0 = agent.data.y[0]
                    t0_dist = np.linalg.norm(np.array([tx,ty])-np.array([ax_t0,ay_t0]))
                    ax_tn = agent.data.x[-1]
                    ay_tn = agent.data.y[-1]
                    tn_dist = np.linalg.norm(np.array([tx,ty])-np.array([ax_tn,ay_tn]))
                    # exp 1
                    # ft = final dist * ( 1 - ratio between initial and final dist )
                    # trial cc: best=1, same_dist=0, farther than d0=negative values
                    # exp 2
                    # trial_cc = (t0_dist-tn_dist)/t0_dist
                    # trial_ft = agent.e/1000 + trial_cc
                    # exp 3
                    trial_ft = agent.e/1000
                    ags_ft_results[enum].append(trial_ft)
                    #print("\nagent{}, trial_ft={}, agent.e={}, trial_cc={}, dist(t=0):{}, dist(t=n):{}".format(enum, round(trial_ft,2), round(agent.e,2), round(trial_cc,2), round(t0_dist,2),round(tn_dist,2)))
                    print("\nagent{}, trial_ft={}, agent.e={}".format(enum, round(trial_ft,2), round(agent.e,2)))

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
            print("\ngeneration {} results:".format(n))
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
            # roulette for parents for remaining genotypes
            total_ft = sum([ba[1] for ba in best_agents])
            while len(self.genotypes) < self.n_agents:
                acum = 0
                rn = np.random.uniform(0,total_ft)
                for px in best_agents:
                    acum += px[1]
                    # <= is necessary for the cases when all die (early generations)
                    if rn <= px[1]:
                        # try to breed if there a better agent
                        y_agents = [px2 for px2 in best_agents if px!=px2]
                        # for cases with few agents
                        if len(y_agents) > 0:
                            yi = np.random.randint(len(y_agents))
                            py = y_agents[yi]
                            if py[1] > px[1]:
                                # crossover breeding
                                self.breed(px[0],py[0])
                                breeds += 1
                                break
                    else:
                        # self mutation
                        self.mutate(px[0])
                        muts += 1
                        # exit from the px selection, to new parent
                        break
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
        self.genotypes.append(new_genotype)

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
        # sensors parameters: vision
        # vision sensors location
        vs_loc = px.vs_loc
        if np.random.uniform(0,1)<self.mut_rate:
            new_vs_loc = []
            for vloc in vs_loc:
                dl = np.random.randint(-2,3)
                new_vloc = vloc+dl
                if new_vloc < -150 or new_vloc > 150:
                    new_vloc = v_loc
                new_vs_loc.append(new_vloc)
            vs_loc = new_vs_loc
        # vision range and theta
        vs_range = px.vs_range
        vs_theta = px.vs_theta
        if np.random.uniform(0,1)<self.mut_rate:
            dv = np.random.randint(-2,3)
            vs_range += dv
            vs_theta -= dv
        vs_range = px.vs_range if vs_range<10 or vs_range>100 else vs_range
        vs_theta = px.vs_theta if vs_range<10 or vs_theta>180 else vs_theta
        # sensors parameters: olf
        # olf sensors location
        olf_loc = px.olf_loc
        if np.random.uniform(0,1)<self.mut_rate:
            new_olf_loc = []
            for oloc in olf_loc:
                dl = np.random.randint(-2,3)
                new_oloc = oloc+dl
                if new_oloc < -150 or new_oloc > 150:
                    new_oloc = oloc
                new_olf_loc.append(new_oloc)
            olf_loc = new_olf_loc
        # olf range and theta
        olf_range = px.olf_range
        olf_theta = px.olf_theta
        if np.random.uniform(0,1)<self.mut_rate:
            do = np.random.randint(-2,3)
            olf_range += do
            olf_theta -= do
        # vis vs olf
        if np.random.uniform(0,1)<self.mut_rate:
            if np.random.choice([True,False]):
                vs_range += 1
                olf_range += -1
            else:
                vs_range += -1
                olf_range += 1
        # check ranges
        olf_range = px.olf_range if olf_range<10 or olf_range>100 else olf_range
        olf_theta = px.olf_theta if olf_range<10 or olf_theta>270 else olf_theta
        # make new genotype and return
        new_genotype = min_genotype.Genotype(vs_loc=vs_loc, vs_range=vs_range, vs_theta=vs_theta, olf_loc=olf_loc, olf_range=olf_range, olf_theta=olf_theta, n_hidden=px.n_hidden, network=px.network)
        self.genotypes.append(new_genotype)

    # def breed(self, px, py):
    #     # new weights shape
    #     parents = [px,py]
    #     pw = parents[np.random.randint(0,2)]
    #     wshape = pw.W.shape[0]
    #     # crossover (for each unit connections)
    #     W = np.array([])
    #     for i in range(wshape):
    #         pi = parents[np.random.randint(0,2)]
    #         # in case chosen shape has more rows than chosen pi
    #         if len(pi.W) >= i:
    #             wi = pi.W[i]
    #         else:
    #             wi = px.W[i] if len(px.W) > len(py.W) else py.W[i]
    #         # in case chosen row has different n of elements than chosen shape
    #         if len(wi) > wshape:
    #             wi = wi[:wshape]
    #         elif len(wi) < wshape:
    #             wi = np.concatenate((wi, np.array([0.5]*(wshape-len(wi)))))
    #         # append
    #         W = np.concatenate((W,wi))
    #     # reshape
    #     W = W.reshape(wshape,wshape)
    #     # thresholds
    #     pi = parents[np.random.randint(0,2)]
    #     ut = pi.ut
    #     pi = parents[np.random.randint(0,2)]
    #     lt = pi.lt
    #     # hidden units (not changes in input/output units for now)
    #     nhu = pw.n_hidden
    #     # new genotype
    #     new_genotype = min_genotype.Genotype(n_hidden=nhu, ut=ut, lt=lt, W=W)
    #     self.genotypes.append(new_genotype)
    #
    # def mutate(self, px):
    #     # mutate weights
    #     wx = px.W
    #     for i in range(len(wx)):
    #         for j in range(len(wx[i])):
    #             if np.random.uniform(0,1)<self.mut_rate:
    #                 wx[i][j] += np.random.uniform(-0.1,0.1)
    #     # check ranges
    #     wx = np.where(wx<0,0, np.where(wx>1,1, wx))
    #     # hidden units number
    #     nhu = px.n_hidden
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         nhu += np.random.choice([-1,1])
    #     nhu = 2 if nhu < 2 else nhu
    #     nhu = 5 if nhu > 5 else nhu
    #     # thresholds
    #     lt = px.lt
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         lt += np.random.uniform(-0.05,0.05)
    #     ut = px.ut
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         ut += np.random.uniform(-0.05,0.05)
    #     # check thresholds
    #     lt = px.lt if lt<0.05 or lt>ut-0.1 else lt
    #     ut = px.ut if ut<lt+0.1 or ut>0.95 else ut
    #     # sensors parameters: vision
    #     # vision sensors location
    #     vs_loc = px.vs_loc
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         new_vs_loc = []
    #         for vloc in vs_loc:
    #             dl = np.random.randint(-2,3)
    #             new_vloc = vloc+dl
    #             if new_vloc < -150 or new_vloc > 150:
    #                 new_vloc = v_loc
    #             new_vs_loc.append(new_vloc)
    #         vs_loc = new_vs_loc
    #     # vision range and theta
    #     vs_range = px.vs_range
    #     vs_theta = px.vs_theta
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         dv = np.random.randint(-2,3)
    #         vs_range += dv
    #         vs_theta -= dv
    #     vs_range = px.vs_range if vs_range<10 or vs_range>100 else vs_range
    #     vs_theta = px.vs_theta if vs_range<10 or vs_theta>180 else vs_theta
    #     # sensors parameters: olf
    #     # olf sensors location
    #     olf_loc = px.olf_loc
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         new_olf_loc = []
    #         for oloc in olf_loc:
    #             dl = np.random.randint(-2,3)
    #             new_oloc = oloc+dl
    #             if new_oloc < -150 or new_oloc > 150:
    #                 new_oloc = oloc
    #             new_olf_loc.append(new_oloc)
    #         olf_loc = new_olf_loc
    #     # olf range and theta
    #     olf_range = px.olf_range
    #     olf_theta = px.olf_theta
    #     if np.random.uniform(0,1)<self.mut_rate:
    #         do = np.random.randint(-2,3)
    #         olf_range += do
    #         olf_theta -= do
    #     olf_range = px.olf_range if olf_range<10 or olf_range>100 else olf_range
    #     olf_theta = px.olf_theta if olf_range<10 or olf_theta>270 else olf_theta
    #     # not changing input/output number of units
    #     # vs_n
    #     # olf_n
    #     # new genotype
    #     new_genotype = min_genotype.Genotype(vs_loc=vs_loc, vs_range=vs_range, vs_theta=vs_theta, olf_loc=olf_loc, olf_range=olf_range, olf_theta=olf_theta, n_hidden=nhu, ut=ut, lt=lt, W=wx)
    #     self.genotypes.append(new_genotype)

    def save_sim(self, filename="temp"):
        # filename and path
        i_filename = "{}_{}_{}_ags={}_t={}_gen={:03}.obj".format(filename,self.index,self.description,self.n_agents,self.trial_t,len(self.best_cases))
        if not os.path.isdir(self.dir_path):
            os.mkdir(self.dir_path)
        i_path = os.path.join(self.dir_path,i_filename)
        # look for previous temps
        temps = [i for i in os.listdir(self.dir_path) if self.index in i]
        # check if file already exists
        if os.path.isfile(i_path):
            print("file already exists at {}".format(i_path))
            import time
            i_filename += "_{}".format(time.ctime())
            i_path = os.path.join(self.dir_path,i_filename)
        # save with pickle
        with open(i_path, "wb") as exp_file:
            pickle.dump(self.best_cases, exp_file)
        print("\n{} object saved at: \n{}".format(i_filename, i_path))
        # remove previous versions if finished (except last one, just in case)
        if filename != "temp" or len(temps)>5:
            for tempfile in temps[:-1]:
                os.remove(os.path.join(self.dir_path,tempfile))
                print("removed temporal file: {}".format(tempfile))



Evolve()














    #
