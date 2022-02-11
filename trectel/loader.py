
from ring_system import Ring
from simulation import trial
from ring_animation import animation_fx
import numpy as np
import pickle
import os

def load(wdir="ring_exps",ext="rxs",default=True,anim=True,save_video=False,return_data=False,return_gts=False):
    # search dir
    wdir = os.path.join(os.getcwd(),wdir)
    try:
        objs = sorted([i for i in os.listdir(wdir) if ext in i])
        select_obj = True
    except:
        print("something's wrong with: {}".format(wdir))
        select_obj = False
    if len(objs)==0:
        print("didn't find objects at dir: {}".format(wdir))
        select_obj = False
    # display objects
    problem_select_obj=" "
    while select_obj == True:
        # display files
        print("")
        for enum, obj_filename in enumerate(objs):
            print("{} - {}".format(enum, obj_filename))
        print("\n\"q\" to quit")
        # in case of
        print("{}".format(problem_select_obj))
        problem_select_obj=" "
        # # select object manually
        if default==True:
            # optional auto select last object
            n_in = len(objs)-1
            print("==> auto selected {}\n".format(objs[n_in]))
        else:
            n_in = input("\nselect object: ")
        # options (just pdb, quit and continue here)
        if n_in=="-pdb" or n_in=="--pdb":
            import pdb; pdb.set_trace()
        elif n_in=="q" or n_in=="-q" or n_in=="quit":
            select_obj=False
            gt_menu=False
        else:
            try:
                # load object
                n_obj = int(n_in)
                n_obj_filename = objs[n_obj]
                obj_path = os.path.join(wdir,n_obj_filename)
                with open(obj_path, "rb") as ea_exp:
                    loaded_obj = pickle.load(ea_exp)
                gt_menu=True
                # optional return to work with the data
                if return_data==True:
                    return loaded_obj
                # data : [wft, genotype, [fi1,fi2,fi3,fi4]]
                if return_gts==True:
                    genotypes = [gi[1] for gi in loaded_obj]
                    return genotypes,n_obj_filename
            except:
                problem_select_obj="\ncouldn't open object, invalid input? --pdb for the pdb.set_trace()\n"
                gt_menu=False
        # select glider
        if gt_menu==True:
            # simulation parameters
            sim_speed = 1000
            world_size = 25
            world_th=0.2
            trial_steps = 100
            problem_gt_menu=" "
            while gt_menu==True:
                g_in = 0
                print("")
                # genotypes
                print('\n{} genotypes loaded, current gt: {}\n'.format(len(loaded_obj),g_in))
                # TODO
                # print('\'-n\' to run and sort them all')
                print("\"-anim\" to (de)active the animation, currently: {}".format("ON" if anim==True else "OFF"))
                print("\"-save\" to (de)active save video, currently: {}".format("ON" if save_video==True else "OFF"))
                print("\"-ss\" to change simulation step interval (speed), currently: {}".format(sim_speed))
                print("\"-ws\" to change world size, currently: {}".format(world_size))
                print("\"-wt\" to change world th, currently: {}".format(world_th))
                print("\"-tt\" to change trial time, currently: {}".format(trial_steps))
                print("\nreturn to go on")
                print("\"-pdb\" for pdb")
                print("\"-x\" to go back")
                print("\"-q\" to go quit")
                # just in case
                print("{}".format(problem_gt_menu))
                problem_gt_menu=" "
                # auto select last object
                if default==True:
                    g_in = 0
                    print("\n==> auto selected gt{}\n".format(0))
                    default=False
                else:
                    gt_menu_in = input("> ")
                    g_in = gt_menu_in if gt_menu_in != '' else g_in
                # options
                if g_in=="-pdb" or g_in=="--pdb":
                    import pdb; pdb.set_trace()
                elif g_in=="-anim" or g_in=="anim":
                    anim=True if anim==False else True
                elif g_in=="-save" or g_in=="save":
                    save_video=True if save_video==False else True
                elif g_in=="ws" or g_in=="-ws":
                    try:
                        sim_speed = int(input("world size? > "))
                    except:
                        print("invalid input: {}".format(sim_speed))
                elif g_in=="ws" or g_in=="-ws":
                    try:
                        world_size = int(input("world size? > "))
                    except:
                        print("invalid input: {}".format(world_size))
                elif g_in=="wt" or g_in=="-wt":
                    try:
                        world_th = int(input("world filling threshold? >  "))
                    except:
                        print("invalid input: {}".format(world_th))
                elif g_in=="tt" or g_in=="-tt":
                    try:
                        trial_steps = int(input("number of trial steps? > "))
                    except:
                        print("invalid input: {}".format(trial_steps))
                elif g_in=="x" or g_in=="-x" or g_in=="back":
                    gt_menu=False
                elif g_in=="q" or g_in=="-q" or g_in=="quit":
                    gt_menu=False
                    select_obj=False
                # animation
                else:
                    try:
                        gtx = loaded_obj[g_in]
                        animation_fx(gtx,show=anim,save=save_video,sim_speed=sim_speed,trial_steps=trial_steps,world_size=world_size,world_th0=world_th)
                    except:
                        problem_gt_menu="\ncouldn't load data, invalid input? ({}) --pdb for the pdb.set_trace()".format(gt_menu_in)



#load()





























#
