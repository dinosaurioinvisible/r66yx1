
from simulations import ring_gol_trial
from animations import ringb_animation
import pickle
import numpy as np
import os
import sys

# basic loading function with menu
def load(wdir="ring_exps",ext="rx",auto=True,return_gts=False,animation=True,save_animation=False):
    # search dir
    wdir = os.path.join(os.getcwd(),wdir)
    try:
        objs = sorted([i for i in os.listdir(wdir) if ext in i])
        select_obj = True
    except:
        print("something's wrong with: {}".format(wdir))
        select_obj = False
    if len(objs)==0:
        print("\ndidn't find \'.{}\' objects at dir: {}".format(ext,wdir))
        select_obj = False
    # display objects
    problem_select_obj=" "
    while select_obj == True:
        # display files
        print("")
        for enum, obj_filename in enumerate(objs):
            print("{} - {}".format(enum, obj_filename))
        print("\n\"-pdb\" for pdb")
        print("\"q\" to quit")
        # in case of
        print("{}".format(problem_select_obj))
        problem_select_obj=""
        # select object manually
        if auto==True:
            # optional auto select last object
            n_in = len(objs)-1
            print("==> auto selected {} - {}\n".format(n_in,objs[n_in]))
        else:
            n_in = input("\n> ")
        # options (just pdb, quit and continue here)
        if n_in=="pdb":
            import pdb; pdb.set_trace()
            gt_menu=False
        elif n_in=="q" or n_in=="quit":
            select_obj=False
            gt_menu=False
        else:
            try:
                # load object
                n_obj = int(n_in)
                n_obj_filename = objs[n_obj]
                obj_path = os.path.join(wdir,n_obj_filename)
                with open(obj_path, "rb") as ea_exp:
                    genotypes = pickle.load(ea_exp)
                if return_gts:
                    return genotypes,n_obj_filename
                gt_menu=True
            except:
                problem_select_obj="\ncouldn't open object, invalid input? --pdb for the pdb.set_trace()\n"
                gt_menu=False
        # select glider
        if gt_menu==True:
            # parameters
            sim_speed = 2000
            min_sim_speed = 50
            max_sim_speed = 2500
            world_size = 25
            min_world_size = 11
            max_world_size = 101
            world_th0= 0.3
            min_world_th0 = 0
            max_world_th0 = 0.9
            timesteps = 100
            min_timesteps = 10
            max_timesteps = 9999
            problem_gt_menu=""
            g_in = 0
            # display menu
            while gt_menu==True:
                print("")
                ring_load = False
                # genotypes
                g_in = g_in if type(g_in)==int and 0<=g_in<len(genotypes) else 0
                print('\n{} genotypes loaded from: {}\n'.format(len(genotypes),n_obj_filename))
                print("\"gt\" to change genotype, current gt: {}".format(g_in))
                print("\"x\" to return genotypes")
                # animation
                print("\"anim\" to (de)active the animation, currently: {}".format("ON" if animation==True else "OFF"))
                print("\"save anim\" to (de)active save video, currently: {}".format("ON" if save_animation==True else "OFF"))
                print("\"ss\" to change simulation step interval (anim. speed), currently: {}".format(sim_speed))
                # simulation parameters
                print("\"ws\" to change world size, currently: {}".format(world_size))
                print("\"wt\" to change world th, currently: {}".format(world_th0))
                print("\"tt\" to change trial timesteps, currently: {}".format(timesteps))
                # auto
                print("\"pdb\" for pdb")
                print("\"b\" to go back")
                print("\"q\" to quit")
                print("return to continue to simulation")
                # for invalid inputs
                print("\n{}\n".format(problem_gt_menu))
                problem_gt_menu=""
                # auto select last object
                if auto==True:
                    g_in = 0
                    print("\n==> auto selected gt{}\n".format(0))
                    auto=False
                else:
                    gt_menu_in = input("> ")
                    g_in = gt_menu_in if gt_menu_in != '' else g_in
                # options: change current gt object
                if g_in=="gt":
                    gt_in = input("genotype? (0:{}) > ".format(len(genotypes)-1))
                    try:
                        if 0<=int(gt_in)<len(genotypes):
                            g_in = int(gt_in)
                        else:
                            problem_gt_menu = "there are {} loaded genotypes (0:{}); input given: {}".format(len(genotypes),len(genotypes)-1,gt_in)
                    except:
                        problem_gt_menu = "there are {} loaded genotypes (0:{}); input given: {}".format(len(genotypes),len(genotypes)-1,gt_in)
                # options: return genotypes
                elif g_in=="x" or g_in=="return":
                    return genotypes
                # options: pdb
                elif g_in=="pdb":
                    import pdb; pdb.set_trace()
                # options: animation
                elif g_in=="anim":
                    animation=True if animation==False else False
                # options: save animation
                elif g_in=="save anim" or g_in=="save-anim":
                    save_animation=True if save_animation==False else False
                # options: simulation speed (frames per second)
                elif g_in=="ss":
                    ss_in = input("sim speed? (100:2500) > ")
                    try:
                        if min_sim_speed<=int(ss_in)<=max_sim_speed:
                            sim_speed = int(ss_in)
                        else:
                            problem_gt_menu = "sim speed must be a integer between {} and {}; input given: {}".format(min_sim_speed,max_sim_speed,ss_in)
                    except:
                        problem_gt_menu = "sim speed must be a integer between {} and {}; input given: {}".format(min_sim_speed,max_sim_speed,ss_in)
                # options: world size
                elif g_in=="ws":
                    ws_in = input("world size? > ")
                    try:
                        if min_world_size<=int(ws_in)<=max_world_size:
                            world_size = int(ws_in)
                        else:
                            problem_gt_menu = "world size must be an integer between {} and {}; input given: {}".format(min_world_size,max_world_size,ws_in)
                    except:
                        problem_gt_menu = "world size must be an integer between {} and {}; input given: {}".format(min_world_size,max_world_size,ws_in)
                # options: world initial threshold for filling
                elif g_in=="wt":
                    wt_in = input("world init filling threshold? >  ")
                    try:
                        if min_world_th0<=float(wt_in)<=max_world_th0:
                            world_th0 = float(wt_in)
                        else:
                            problem_gt_menu = "world init threshold must a float between {} and {}; input given: {}".format(min_world_th0,max_world_th0,wt_in)
                    except:
                        problem_gt_menu = "world init threshold must a float between {} and {}; input given: {}".format(min_world_th0,max_world_th0,wt_in)
                # options: timesteps
                elif g_in=="tt":
                    tt_in = input("number of timesteps? > ")
                    try:
                        if min_timesteps<=int(tt_in)<=max_timesteps:
                            timesteps = int(tt_in)
                        else:
                            problem_gt_menu = "timesteps must be an integer between {} and {}; input given: {}".format(min_timesteps,max_timesteps,tt_in)
                    except:
                        problem_gt_menu = "timesteps must be an integer between {} and {}; input given: {}".format(min_timesteps,max_timesteps,tt_in)
                # options: go back or quit
                elif g_in=="b" or g_in=="-b" or g_in=="back":
                    gt_menu=False
                elif g_in=="q" or g_in=="-q" or g_in=="quit":
                    gt_menu=False
                    select_obj=False
                # try to load object
                else:
                    #try:
                    if 1==1:
                        gtx = genotypes[g_in]
                        ring,ft,trial_data = ring_gol_trial(ring_gt=gtx,timesteps=timesteps,world_size=world_size,world_th0=world_th0,save_data=True)
                        print("\nfitness = {}".format(round(ft,4)))
                        ring_load = True
                    #except:
                    else:
                        problem_gt_menu="couldn't run simulation (input: {}) --pdb for the pdb.set_trace()".format(g_in)
                    # load and run
                    if ring_load:
                        # animation
                        if animation:
                            ringb_animation(ring,ft,trial_data,sim_speed=sim_speed,save_animation=save_animation)
                        # in case return data is false
                        ask_after_sim = True
                        after_sim_menu_problem = ""
                        while ask_after_sim == True:
                            print("\n\'anim\' to animate again")
                            print("\'s\' to save data (pickle)")
                            print("\'x\' to return data")
                            print("\'pdb\' for pdb")
                            print("\'b\' to go back")
                            print("\'q\' to quit")
                            print(after_sim_menu_problem)
                            after_sim_in = input("\n > ")
                            if after_sim_in=="s" or after_sim_in=="save":
                                data = [ring,ft,trial_data]
                                filename = "loadsim_ft={}_file={}".format(round(ft,2),n_obj_filename)
                                filepath = os.path.join(self.path,filename)
                                if os.path.isfile(filepath):
                                    dx_name = input('file already exists, new name? > ')
                                    filename = "loadsim_ft={}_file={}_{}".format(round(ft,2),n_obj_filename,dx_name)
                                    filepath = os.path.join(self.path,filename)
                                with open(filepath,'wb') as datapath:
                                    pickle.dump(data,datapath)
                                print("\nsaved at: {}".format(filepath))
                            elif after_sim_in == "x" or after_sim_in=="return":
                                return ring,ft,trial_data
                            elif after_sim_in == "anim":
                                ringb_animation(ring,ft,trial_data,sim_speed=sim_speed,save_animation=save_animation)
                            elif after_sim_in == "pdb":
                                print("\nvars: ring, ft, trial_data\n")
                                import pdb; pdb.set_trace()
                            elif after_sim_in=="b" or after_sim_in=="back":
                                ask_after_sim = False
                            elif after_sim_in=="q" or after_sim_in=="quit":
                                ask_after_sim=False
                                gt_menu=False
                                select_obj=False
                            else:
                                after_sim_menu_problem = "\ninvalid input ({})".format(after_sim_in)


auto_run = sys.argv[1] if len(sys.argv)>1 else None
auto_load = sys.argv[2] if len(sys.argv)>2 else None
file_ext = sys.argv[3] if len(sys.argv)>3 else None
if sys.argv[0]=='loader.py':
    if auto_run:
        if auto_load:
            if file_ext:
                load(auto=auto_load,ext=file_ext)
            else:
                load(auto=auto_load)
        else:
            load()





























#
