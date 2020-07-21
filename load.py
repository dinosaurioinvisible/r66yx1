import os
import pickle
import _trial
import _trial_animation
import matplotlib.pyplot as plt
import numpy as np
import seaborn

def load(filename, anim=True, hmap=True, ret=True):
    path = os.path.join(os.getcwd(), filename)
    with open(path, "rb") as ea_exp:
        xobj = pickle.load(ea_exp)
    on = True
    while on == True:
        print("")
        for enum, case in enumerate(xobj.good_cases):
            print("{} - gen: {}, fitness: {}".format(enum, case[0], case[1]))
        print("\"h\" for enabling/disabling heatmap, currently: {}".format("ON" if hmap else "OFF"))
        print("\"a\" for enabling/disabling animation, currently: {}".format("ON" if anim else "OFF"))
        print("\"q\" for exit")
        n_in = input("\nshow? : ")
        if n_in=="q" or n_in=="quit":
            on = False
        elif n_in == "a":
            anim = False if anim == True else True
        elif n_in == "h":
            hmap = False if hmap == True else True
        else:
            try:
                nx = int(n_in)
                xgen = xobj.good_cases[nx][2]
                show_anim = anim
                show_hmap = hmap
            except:
                print("invalid input")
                show_anim = False
                show_hmap = False
            # trial and animation
            if show_anim:
                xtrial = _trial.Trial(t=1000, genotype=xgen, n_agents=1, world=None, n_trees=10, n_walls=4)
                _trial_animation.sim_animation(xtrial.world, xtrial.agents, xtrial.t)
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
