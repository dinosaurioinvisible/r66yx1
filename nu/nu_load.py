
import os
import pickle
from nu_trial import Trial

def load(fdir="glxs",anim=True,save=False,netplot=True):
    wdir = os.path.join(os.getcwd(),fdir)
    glxs_files = sorted([i for i in os.listdir(wdir) if "glxs" in i])
    select_file=True
    while select_file==True:
        print("\n")
        select_glx=False
        for fi,glf in enumerate(glxs_files):
            print("{} - {}".format(fi,glf))
        print("q to quit")
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
        sort_by="cycles"
        while select_glx==True:
            print("\n")
            glx=None
            for gi,gl in enumerate(glxs[:glxs_show]):
                print("{} - cycles={}, dashes={}".format(gi,len(gl.cycles),len(gl.kdp)))
            print("\n[a]nim={}, [s]ort by={}, [n]etplot={}, [all], [q]uit".format(anim,sort_by,netplot))
            ngl = input("\n glx? _")
            if ngl=="a":
                anim = True if anim==False else False
            elif ngl=="s":
                sort_by = "dashes" if sort_by=="cycles" else "dashes"
                if sort_by=="dashes":
                    glxs = sorted(glxs,key=lambda x:x.kdp,reverse=True)
                else:
                    glxs = sorted(glxs,key=lambda x:len(x.cycles),reverse=True)
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
                print("\nknown dashes = {}: \n{}".format(len(glx.kdp),glx.kdp))
                print("\ncycles:")
                for cy,cycle in enumerate(glx.cycles):
                    print(cy,cycle)
                glx_trial = Trial(auto=True,gtx=glx,mode="full",anim=anim,plot=netplot)


load()








###
