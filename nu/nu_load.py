
import os
import pickle
from nu_trial import Trial
from nu_animation import glx_anim

def load(fdir="glxs",anim=True,save=False,netplot=True,auto=False):
    wdir = os.path.join(os.getcwd(),fdir)
    glxs_files = sorted([i for i in os.listdir(wdir) if "glxs" in i])
    select_file=True
    while select_file==True:
        print("\n")
        select_glx=False
        for fi,glf in enumerate(glxs_files):
            print("{} - {}".format(fi,glf))
        print("q to quit")
        if auto:
            nf=41
        else:
            nf = input("\n gl file? _ ")
        if nf=="q":
            select_file=False
        else:
            try:
                gfile = os.path.join(wdir,glxs_files[int(nf)])
                with open(gfile,"rb") as glxs_file:
                    glxs = pickle.load(glxs_file)
                select_glx=True
            except:
                print("couldn't open file {}".format(nf))
        glxs_show=10
        sort_by="txs"
        while select_glx==True:
            print("\n")
            glx=None
            for gi,gl in enumerate(glxs[:glxs_show]):
                print("{} - txs={}, gt_size={}, dashes={}".format(gi,len(gl.txs),len(gl.exgt),len(gl.dxs)))
            print("\n[a]nim={}, [s]ort by={}, [n]etplot={}, [all], [q]uit".format(anim,sort_by,netplot))
            if auto:
                ngl=0
            else:
                ngl = input("\n glx? _")
            if ngl=="a":
                anim = True if anim==False else False
            elif ngl=="s":
                sort_by = "dashes" if sort_by=="txs" else "txs"
                if sort_by=="dashes":
                    glxs = sorted(glxs,key=lambda x:x.dxs,reverse=True)
                else:
                    glxs = sorted(glxs,key=lambda x:len(x.txs),reverse=True)
            elif ngl=="n":
                netplot = True if netplot==False else False
            elif ngl=="all":
                glxs_show=len(glxs)
            elif ngl=="q":
                select_glx=False
            else:
                try:
                    glx = glxs[int(ngl)]
                except:
                    print("\ncouldn't open {}".format(ngl))
            if glx:
                print("\n\nglx pdb")
                if anim==True or save==True:
                    glx_trial = Trial(auto=True,gtx=glx,mode="full",anim=anim)
                    import pdb; pdb.set_trace()
            auto = False

load("glxs_run=001",auto=True)





###
