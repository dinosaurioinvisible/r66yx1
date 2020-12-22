
import os
import pickle
import min_trial
import min_animation
import matplotlib.pyplot as plt
import numpy as np

def load(wdir="min_objs", trial_time=500, n_agents=5, wsize=500, n_trees=10, n_walls=4, anim=True, video=False, x_agent=False, ret=False):
    try:
        wdir = os.path.join(os.getcwd(), wdir)
    except:
        print("didn't find working dir: {}".format(wdir))
        wdir = os.getcwd()
    objs = sorted([i for i in os.listdir(wdir) if ".obj" in i])
    select = True
    # select object
    while select == True:
        on = False
        print("\n")
        for enum, obj_filename in enumerate(objs):
            print("{} : {}".format(enum, obj_filename))
        print("\"q\" to quit")
        n_in = input("\nselect object: ")
        if n_in=="q" or n_in=="quit":
            select = False
        else:
            try:
                n_obj = int(n_in)
                n_obj_filename = objs[n_obj]
                obj_path = os.path.join(wdir, n_obj_filename)
                with open(obj_path, "rb") as ea_exp:
                    xobj = pickle.load(ea_exp)
                cases = xobj
                on = True
            except:
                print("couldn't open object")
        # select generation
        while on == True:
            print("\n")
            for enum, case in enumerate(cases):
                ax_ft = [ag[1] for ag in cases[enum]]
                print("gen {}, fts: {}".format(enum, np.around(ax_ft,2)))
            print("\n")
            #print("\"hmap\" for enabling/disabling heatmap, currently: {}".format("ON" if hmap else "OFF"))
            print("\"anim\" for enabling/disabling animation, currently: {}".format("ON" if anim else "OFF"))
            print("\"vid\" for enabling/disabling saving the animation, currently: {}".format("ON" if video else "OFF"))
            print("\"plot\" to plot fitness evolution")
            print("\"aa\" to add an agent \"ra\" to remove one, currently: {}".format(n_agents))
            print("\"tr\" for changing number of trees, currently: {}".format(n_trees))
            print("\"tt\" for changing trial timesteps, currently: {}".format(trial_time))
            print("\"w\" for changing the world size, currently: {}x{}".format(wsize,wsize))
            print("\"x\" for enabling/disabling specific agent selection, currently: {}".format("ON" if x_agent else "OFF"))
            print("\"c\" to compare genotypes")
            print("\"ret\" to return list of results and genotypes")
            print("\"q\" for exit")
            # do as input
            n_in = input("\nshow? : ")
            if n_in=="q" or n_in=="quit":
                on = False
            elif n_in=="ret":
                return cases
            elif n_in=="plot":
                plt.plot(np.arange(0,len(cases)),np.asarray([sum([ag[1] for ag in case]) for case in cases]))
                plt.xlabel("Generation")
                plt.ylabel("Fitness")
                plt.show()
            elif n_in == "aa":
                n_agents += 1
            elif n_in == "ra":
                n_agents -= 1
                n_agents = 1 if n_agents < 1 else n_agents
            elif n_in == "tr":
                try:
                    n_trees = int(input("\nnumber of trees? : "))
                    n_trees = 1 if n_trees < 1 else n_trees
                except:
                    print("invalid input")
            elif n_in == "tt":
                try:
                    trial_time = int(input("\ntimesteps? : "))
                except:
                    print("invalid input")
            elif n_in == "w":
                try:
                    wsize = int(input("\nworld size (square)? : "))
                except:
                    print("invalid input")
            elif n_in=="anim":
                anim = False if anim==True else True
            elif n_in=="vid" or n_in=="video":
                video = False if video==True else True
            elif n_in=="x":
                x_agent = False if x_agent==True else True
            # elif n_in=="hmap":
            #     hmap = False if hmap==True else True
            elif n_in=="c" or n_in=="compare":
                gg_comp = True
                manual_comp = False
                while gg_comp == True:
                    print("\nchoose genotypes to compare (generation, individual)")
                    print("\"man\" to activate/deact manual comparison (pdb), currently: {}".format("ON" if manual_comp==True else "OFF"))
                    print("\"q\" to go up out")
                    g1_input = input("G1 generation,individual ?: ")
                    if g1_input=="q" or g1_input=="quit":
                        gg_comp = False
                    elif g1_input=="m" or g1_input=="man":
                        manual_comp = True
                    else:
                        g2_input = input("G2 generation,individual ?: ")
                        if g2_input=="q" or g2_input=="quit":
                            gg_comp = False
                        else:
                            try:
                                g1_gen, g1_ind = g1_input.split(",")
                                g2_gen, g2_ind = g2_input.split(",")
                                g1, g1_ft = cases[int(g1_gen)][int(g1_ind)]
                                g2, g2_ft = cases[int(g2_gen)][int(g2_ind)]
                                print("{},{}: g1={}, ft={}".format(g1_gen,g1_ind,g1,round(g1_ft,2)))
                                print("{},{}: g2={}, ft={}".format(g2_gen,g2_ind,g2,round(g2_ft,2)))
                                print("vision (loc,range,theta): g1=({},{},{}) - g2=({},{},{})".format(g1.vs_loc,g1.vs_range,g1.vs_theta ,g2.vs_loc,g2.vs_range,g2.vs_theta))
                                print("olfact (loc,range,theta): g1=({},{},{}) - g2=({},{},{})".format(g1.olf_loc,g1.olf_range,g1.olf_theta, g2.olf_loc,g2.olf_range,g2.olf_theta))
                                print("g1 network thresholds:\n {}".format(np.around([[nx.lt,nx.ut] for nx in g1.network],2)))
                                print("g2 network thresholds:\n {}".format(np.around([[nx.lt,nx.ut] for nx in g2.network],2)))
                                wg1 = np.around(np.array([nx.wx for nx in g1.network]),2)
                                wg2 = np.around(np.array([nx.wx for nx in g2.network]),2)
                                print("\n{}".format(wg1))
                                print("\n{}".format(wg2))
                                if manual_comp == True:
                                    import pdb; pdb.set_trace()
                                    manual_comp = False
                            except:
                                print("invalid input (format example: 45,6)")
            else:
                try:
                    nx = int(n_in)
                    xgen = [ag[0] for ag in cases[nx]]
                    show_anim = anim
                    # less agents than genotypes
                    if n_agents < len(xgen):
                        xgen = xgen[:n_agents]
                    # specific agent selection
                    if x_agent:
                        print("showing {}/{}:".format(n_agents,len(cases[nx])))
                        print("{}".format([[i,round(cases[nx][i][1],2)] for i in range(len(cases[nx][:n_agents]))]))
                        n_ag = input("agent?: ")
                        n_agent = int(n_ag)
                        xgen = xgen[n_agent]
                except:
                    print("\ninvalid index input")
                    show_anim = False
                    show_hmap = False
                # show_hmap = hmap
                # animation
                if show_anim:
                    if x_agent:
                        xtrial = min_trial.Trial(t=trial_time, genotypes=xgen, mode="minimal", world=None, world_size=wsize, n_trees=n_trees, n_walls=n_walls)
                    else:
                        xtrial = min_trial.Trial(t=trial_time, genotypes=xgen, world=None, world_size=wsize, n_trees=n_trees, n_walls=n_walls)
                    min_animation.sim_animation(xtrial.world, xtrial.agents, xtrial.t, video=video)

# load()
























#
