
import numpy as np
import qeval
import matplotlib.pyplot as plt
import pickle
import qanim
import os


def load(wdir="qobjs", default=False, time=300, reps=1, wsize=500, anim=True, video=False, ret=False):
    # search dir
    try:
        wdir = os.path.join(os.getcwd(), wdir)
        objs = sorted([i for i in os.listdir(wdir) if "obj" in i])
        select_obj = True
    except:
        print("didn't find objects at dir: {}".format(wdir))
        select_obj = False
    # display objects
    select_gen = False
    while select_obj == True:
        print("\n")
        for enum, obj_filename in enumerate(objs):
            print("{} - {}".format(enum, obj_filename))
        print("\n\"q\" to quit")
        # auto select last object
        if default==True:
            n_in = len(objs)-1
            print("\n==> auto selected {}".format(objs[n_in]))
        else:
            # select object
            n_in = input("\nselect object: ")
        if n_in=="q" or n_in=="quit":
            select_gen = False
            select_obj = False
        else:
            try:
                n_obj = int(n_in)
                n_obj_filename = objs[n_obj]
                obj_path = os.path.join(wdir, n_obj_filename)
                with open(obj_path, "rb") as ea_exp:
                    generations = pickle.load(ea_exp)
                select_gen = True
            except:
                print("couldn't open object")
        # display generations
        select_gt = False
        while select_gen==True:
            print("\n")
            for enum,gen in enumerate(generations):
                fts = [gt[1] for gt in generations[enum]]
                avft = sum(fts)/len(fts)
                print("gen {}, av_gen_ft={}, fts: {}..".format(enum, round(avft,2), np.around(fts[:5],2)))
            print("\n")
            print("\"anim\" for enabling/disabling animation, currently: {}".format("ON" if anim else "OFF"))
            print("\"video\" for enabling/disabling video save, currently: {}".format("ON" if video else "OFF"))
            print("\"plot\" for plot fitness evolution")
            print("\"ret\" to return the object at the end, currently: {}".format("ON" if ret else "OFF"))
            print("\"q\" to exit back")
            # auto select last generation
            if default==True:
                n_gen = len(generations)-1
                print("\n==> auto selected generation {}".format(n_gen))
            else:
                # select generation
                n_gen = input("\ngeneration?: ")
            if n_gen=="q":
                select_gen=False
                select_gt = False
            elif n_gen=="anim" or n_gen=="animation":
                anim=False if anim==True else True
            elif n_gen=="vid" or n_gen=="video":
                video=False if video==True else True
            elif n_gen=="plot":
                plt.plot(np.arange(0,len(generations)),np.asarray([sum([gt[1] for gt in gen])/len(gen) for gen in generations]))
                plt.plot(np.arange(0,len(generations)),np.asarray([gen[0][1] for gen in generations]))
                plt.xlabel("Generation")
                plt.ylabel("Fitness")
                plt.show()
            elif n_gen=="ret" or n_gen=="return":
                ret=False if ret==True else True
            else:
                try:
                    nx = int(n_gen)
                    xgen = generations[nx]
                    select_gt = True
                except:
                    print("\ninvalid index input")
                # display genotypes
                while select_gt == True:
                    print("\n")
                    for enum,gt in enumerate(xgen):
                        gt_seq = [gene[0] for gene in gt[0]]
                        print("gt: {}, ft: {}, genotype: {}".format(enum, np.around(gt[1],2), gt_seq))
                    print("\n")
                    # import pdb; pdb.set_trace()
                    print("\"q\" to exit back")
                    # auto select last generation
                    if default==True:
                        n_gt = 0
                        print("\n==> auto selected genotype {}".format(n_gt))
                    else:
                        # select genotype
                        n_gt = input("\ngenotype?: ")
                    if n_gt=="qw" or n_gt=="quit":
                        select_obj = False
                        select_gen = False
                        select_gt = False
                    elif n_gt=="q":
                        select_gt=False
                    elif n_gt=="ex" or n_gt=="exam":
                        examine = False if examine == True else True
                    else:
                        # run trials
                        try:
                            ngt = int(n_gt)
                            xgt = xgen[ngt][0]
                            show_anim = anim
                            save_vid = video
                        except:
                            print("invalid input")
                            show_anim = False
                            save_vid = False
                        # animation and video
                        eval = qeval.Evaluation(xgt, time, reps)
                        if show_anim:
                            name = "{}: gen={}, gt={}".format(n_obj_filename,n_gen,n_gt)
                            qanim.sim_animation(eval, show=True, save=save_vid, fname=name)
                        default = False
    if ret==True:
        return generations

load()





























#
