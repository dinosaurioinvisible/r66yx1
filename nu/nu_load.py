
import os
import pickle

def load():
    wdir = os.getcwd()
    gls = sorted([i for i in os.listdir(wdir) if "glxs" in i])
    select = False
    while select==False:
        print("")
        for gi,gl in enumerate(gls):
            print("gl{} - {}".format(gi,gl))
        print("q to quit")
        gl_in = input("\n gl?: ")
        
