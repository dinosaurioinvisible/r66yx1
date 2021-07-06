
import os
import pickle
import numpy as np
from nu_trial import Trial
from nu_animation import glx_anim

def load(fdir="glxs",pdb_check=True,anim=True,save=False,netplot=False,auto=False):
    select_dir=False
    wdir = os.path.join(os.getcwd(),fdir)
    if not os.path.isdir(wdir):
        auto=False
        select_dir=True
    # select directory
    dir_message = None
    while select_dir==True:
        print("")
        glxs_dirs = sorted([i for i in os.listdir(os.getcwd()) if fdir in i])
        for di,gdir in enumerate(glxs_dirs):
            print("{} - {}".format(di,gdir))
        if dir_message:
            print("\n{}".format(dir_message))
            dir_message=None
        n_dir = input("\nworking dir? (key=\"{}\" a:show all, q:quit) _ ".format(fdir))
        if n_dir=="q" or n_dir=="quit":
            return
        elif n_dir=="a" or n_dir=="all":
            fdir=""
        else:
            try:
                wdir = os.path.join(os.getcwd(),glxs_dirs[int(n_dir)])
                select_dir=False
            except:
                dir_message = "invalid option"
    # select exp/run file
    mode = wdir.split("_")[-2].split("=")[-1]
    glxs_files = sorted([i for i in os.listdir(wdir) if "glxs" in i],key=lambda x:int(x.split("=")[-1].split(".")[0]))
    select_file=True
    file_message=None
    while select_file==True:
        print("\n")
        select_glx=False
        for fi,glf in enumerate(glxs_files):
            print("{} - {}".format(fi,glf))
        print("q to quit")
        if file_message:
            print("\n{}".format(file_message))
            file_message=None
        if auto:
            nf=41
        else:
            nf = input("\n gl file? _ ")
        if nf=="q" or nf=="quit":
            select_file=False
        else:
            try:
                gfile = os.path.join(wdir,glxs_files[int(nf)])
                with open(gfile,"rb") as glxs_file:
                    glxs = pickle.load(glxs_file)
                select_glx=True
            except:
                file_message = "invalid selection"
        # select agent
        glxs_show=10
        glx_message=None
        dash=100
        while select_glx==True:
            print("\n")
            glx=None
            if mode=="dashes":
                for gi,gl in enumerate(glxs[:glxs_show]):
                    print("{} - txs={}, gt_size={}, dashes={}".format(gi,len(gl.txs),len(gl.exgt),len(gl.dxs)))
            elif mode=="behavior":
                for gi,[gl,gt_res] in enumerate(glxs[:glxs_show]):
                    dxs = [di+1 for di,dx in enumerate(gt_res[1:]) if dx>0]
                    beh = [np.sum(np.where(gt_res[1:-1]==1,1,0)),np.sum(np.where(gt_res[1:-1]==2,1,0)),np.sum(np.where(gt_res[1:-1]==3,1,0)),np.sum(np.where(gt_res[1:-1]==4,1,0))]
                    print("\n{} = cys={}, memb_rxs={}, core_rxs={}, beh={}, dxs={}: \n{}".format(gi,len(gl.cys),len(gl.memb_rxs),len(gl.core_rxs),beh,gt_res[0],dxs))
            print("\n[p]db={}, [a]nim={}: [d]ash={}, [n]etplot={}, [all], [b]ack, [q]uit".format(pdb_check,anim,dash,netplot))
            if glx_message:
                print("\n{}".format(glx_message))
            if auto:
                ngl=0
            else:
                ngl = input("\n glx? _")
            if ngl=="a" or ngl=="anim":
                anim = True if anim==False else False
            elif ngl=="d" or ngl=="dash":
                new_dash = input("new dash? _ ")
                try:
                    if int(new_dash)>0 and int(new_dash)<128:
                        dash = int(new_dash)
                    else:
                        glx_message = "dash needs to be between 1:127"
                except:
                    glx_message = "invalid dash input"
            elif ngl=="p" or ngl=="pdb":
                pdb_check=True if pdb_check==False else False
            elif ngl=="n" or ngl=="netplot":
                netplot = True if netplot==False else False
            elif ngl=="all":
                glxs_show=len(glxs)
            elif ngl=="b" or ngl=="back":
                select_glx=False
            elif ngl=="q" or ngl=="quit":
                return
            else:
                try:
                    glx = glxs[int(ngl)]
                    if mode=="behavior":
                        glx = glx[0]
                except:
                    glx_message = "can't open {}".format(ngl)
            if glx:
                if pdb_check:
                    print("\n\nglx pdb:\n")
                    import pdb; pdb.set_trace()
                if anim:
                    glx_trial = Trial()
                    glx_trial.behavior(glx,single_dash=dash,anim=anim)
                    glx_trial.full(glx,anim=anim)
                if netplot:
                    pass
                if save:
                    pass
            auto = False

load("glxs_mode=behavior_run=002",pdb_check=False,anim=True,auto=True)





###
