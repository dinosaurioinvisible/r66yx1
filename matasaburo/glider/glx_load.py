
from glx_eval import Evaluation
import glx_animation
import numpy as np
import pickle
import os

def load(wdir="gliders",ext="glx",default=True,anim=True,save_video=False,return_data=False,return_gts=False):
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
            problem_gt_menu=" "
            while gt_menu==True:
                print("")
                # data : [wft, genotype, [fi1,fi2,fi3,fi4]]
                for gi,gi_data in enumerate(loaded_obj[:10]):
                    c1,c2,c3,c4 = np.around(gi_data[2],2)
                    print("gt{}: avft={}, c1={}, c2={}, c2={}, c4={}".format(gi,round(gi_data[0],2),c1,c2,c3,c4))
                print("\n\"-anim\" to (de)active the animation, currently: {}".format("ON" if anim==True else "OFF"))
                print("\"-save\" to (de)active save video, currently: {}".format("ON" if save_video==True else "OFF"))
                print("\"-x\" to go back")
                print("\"-q\" to go quit")
                # just in case
                print("{}".format(problem_gt_menu))
                problem_gt_menu=" "
                # auto select last object
                if default==True:
                    g_in = 0
                    print("==> auto selected gt{}".format(0))
                    default=False
                else:
                    # select object manually
                    g_in = input("\nselect object: ")
                # options
                if g_in=="-pdb" or g_in=="--pdb":
                    import pdb; pdb.set_trace()
                elif g_in=="-anim" or g_in=="anim":
                    anim=True if anim==False else True
                elif g_in=="-save" or g_in=="save":
                    save_video=True if save_video==False else True
                elif g_in=="x" or g_in=="-x" or g_in=="back":
                    gt_menu=False
                elif g_in=="q" or g_in=="-q" or g_in=="quit":
                    gt_menu=False
                    select_obj=False
                # animation
                else:
                    try:
                        g_in = int(g_in)
                        glx_gt = loaded_obj[g_in][1]
                        n_cells = len(glx_gt)
                        evx = Evaluation(time=20)
                        glx_wft,glx_fts,glx_states = evx.gt_eval(glx_gt,return_states=True)
                        glx_animation.glx_anim(glx_states,glx_fts,gt=glx_gt,fname=n_obj_filename,show=anim,save=save_video)
                    except:
                        problem_gt_menu="\ncouldn't load data, invalid input? --pdb for the pdb.set_trace()"




#load()





























#
