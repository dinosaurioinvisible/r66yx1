import os
import pickle
import _trial
import min_trial
import _trial_animation
import min_animation
import matplotlib.pyplot as plt
import numpy as np


def load(wdir_name="min_objs", n_agents=1, n_trees=10, trial_time=100, anim=True, hmap=False, ret=False):
    # choose file menu
    try:
        wdir = os.path.join(os.getcwd(), wdir_name)
    except:
        print("working directory not found")
        wdir = os.getcwd()
    objs = [i for i in os.listdir(wdir) if ".obj" in i]
    select = True
    while select == True:
        on = True
        print("\n")
        for enum, obj_filename in enumerate(objs):
            print("{} : {}".format(enum, obj_filename))
        print("\"q\" to quit")
        n_in = input("\nselect object : ")
        if n_in=="q" or n_in=="quit":
            select = False
        else:
            try:
                n_obj = int(n_in)
                n_obj_filename = objs[n_obj]
                obj_path = os.path.join(wdir, n_obj_filename)
                with open(obj_path, "rb") as ea_exp:
                    xobj = pickle.load(ea_exp)
                try:
                    # old, when saving the whole ea object
                    cases = xobj.good_cases
                except:
                    # object = cases
                    cases = xobj
                # just to be sure
                print("\nobject file: {}".format(obj_filename))
            except:
                print("invalid input")
                on = False
            # display menu
            while on == True:
                # check if clonal or normal GA
                clonal = True if len(cases[0]) == 1 else False
                print("")
                for enum, case in enumerate(cases):
                    if clonal:
                        print("{} - gen: {}, fitness: {}".format(enum, case[0], round(case[1],2)))
                    else:
                        ax_e = [ag[1] for ag in cases[enum]]
                        print("gen: {}, e: {}".format(enum, np.around(ax_e,2)))
                print("\n")
                print("\"h\" for enabling/disabling heatmap, currently: {}".format("ON" if hmap else "OFF"))
                print("\"a\" for enabling/disabling animation, currently: {}".format("ON" if anim else "OFF"))
                print("\"p\" to add an agent \"r\" to remove one, currently: {}".format(n_agents))
                print("\"pt\" to add an agent \"rt\" to remove one, currently: {}".format(n_trees))
                print("\"tt\" for changing trial timesteps, currently: {}".format(trial_time))
                print("\"q\" for exit")
                n_in = input("\nshow? : ")
                if n_in=="q" or n_in=="quit":
                    on = False
                elif n_in == "p":
                    n_agents += 1
                elif n_in == "r":
                    n_agents -= 1
                    n_agents = 1 if n_agents < 1 else n_agents
                elif n_in == "pt":
                    n_trees += 1
                elif n_in == "rt":
                    n_trees -= 1
                    n_trees = 1 if n_trees < 1 else n_trees
                elif n_in == "tt":
                    try:
                        trial_time = int(input("\ntimesteps? : "))
                    except:
                        print("invalid input")
                elif n_in == "a":
                    anim = False if anim == True else True
                elif n_in == "h":
                    hmap = False if hmap == True else True
                else:
                    try:
                        nx = int(n_in)
                        if clonal:
                            xgen = cases[nx][2]
                            xft = round(cases[nx][1],2)
                        else:
                            xgen = [gn[0] for gn in cases[nx]]
                        show_anim = anim
                        show_hmap = hmap
                    except:
                        print("invalid input")
                        show_anim = False
                        show_hmap = False
                    # trial and animation
                    if show_anim:
                        if clonal:
                            xtrial = _trial.Trial(t=trial_time, genotype=xgen, n_agents=n_agents, world=None, n_trees=n_trees, n_walls=4)
                            _animation.sim_animation(xtrial.world, xtrial.agents, xtrial.t, xft)
                        else:
                            xtrial = min_trial.Trial(t=trial_time, genotypes=xgen, world=None, n_trees=n_trees, n_walls=4)
                            min_animation.sim_animation(xtrial.world, xtrial.agents, xtrial.t)
                    # heatmap from selected genotype
                    if show_hmap:
                        weights = xgen.W
                        # input
                        vis_units = ["v{}".format(i+1) for i in range(xgen.vs_n)]
                        # for old versions without those params
                        try:
                            olf_units = ["o".format(i+1) for i in range(xgen.olf_n)]
                            e_units = ["e" for i in range(xgen.e_in)]
                        except:
                            olf_units = ["o"]
                            e_units = ["e"]
                        aud_units = ["a{}".format(i+1) for i in range(xgen.com_len)]
                        input_units = vis_units+olf_units+e_units+aud_units
                        # hidden
                        hidden_units = ["h{}".format(i+1) for i in range(xgen.n_hidden)]
                        # output
                        motor_units = ["m1+", "m1-", "m2+", "m2-"]
                        com_units = ["c{}".format(i+1) for i in range(xgen.com_len)]
                        output_units = motor_units+com_units
                        # names for ticks
                        vx = input_units+hidden_units+output_units
                        fig, ax = plt.subplots(figsize=(10,10))
                        im = ax.imshow(weights)
                        # Create colorbar
                        cbar = ax.figure.colorbar(im, ax=ax)
                        cbar.ax.set_ylabel("heatmap", rotation=-90, va="bottom")
                        # labels for neurons
                        ax.set_xticks(np.arange(len(vx)))
                        ax.set_yticks(np.arange(len(vx)))
                        ax.set_xticklabels(vx)
                        ax.set_yticklabels(vx)
                        plt.setp(ax.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")
                        # inside cell text
                        for i in range(len(weights)):
                            for j in range(len(weights[i])):
                                if weights[i,j] == 0:
                                    wx = ax.text(j,i,str(0), ha="center", va="center", color="black")
                                    # to write the weights, (the image nees to be to large)
                                    # wx = ax.text(j,i,str(round(weights[i,j],2)), ha="center", va="center", color="w")
                        ax.set_title("weights heatmap")
                        fig.tight_layout()
                        plt.show()
    if ret:
        return xobj

load()
