
import os
from shutil import copyfile
import sys
import time

def copy(wdir="iphone de Fernando", dest_dir="foto_copias", cue="media"):
    # assuming wdir is one level deeper
    wdir = os.path.join(os.getcwd(),wdir)
    # source directories (and target dir)
    src_dirs = [os.path.join(wdir,srcdir) for srcdir in os.listdir(wdir) if cue in srcdir]
    dest_dir = os.path.join(os.getcwd(),dest_dir)
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    # dirs to walk through
    c = 0
    error_list = []
    for src_dir in src_dirs:
        print("\nsource dir: {}".format(src_dir))
        # walk: working dir, list of dirs in wdir, list of files
        for dirpath, dirs, files in os.walk(src_dir):
            for f in files:
                # do not copy .DS_Store files
                if not ".DS_Store" in f:
                    # new path for copy
                    dest_fpath = os.path.join(dest_dir,f)
                    fpath = os.path.join(dirpath,f)
                    # check if file already exists
                    i = 0
                    on = True
                    while on == True:
                        # cambiar nombre
                        if os.path.isfile(dest_fpath):
                            # cx = "_copy_"
                            cx = "_{}_".format(dirpath.split("/")[-1].split(".")[0])
                            nf = dest_fpath.split("/")[-1]
                            fname, fext = nf.split(".")
                            if cx in fname:
                                i = int(fname.split("_")[-1])+1
                                fname = fname[:-len(str(i-1))]
                            else:
                                fname += cx
                            nf = "{}{}.{}".format(fname,i,fext)
                            dest_fpath = os.path.join(dest_dir,nf)
                        else:
                            on = False
                    # copiar
                    copyfile(fpath, dest_fpath)
                    c += 1
                    sys.stdout.write("\r{} files copied, working dir: {}, newfile: {}".format(c, dirpath.strip(wdir), dest_fpath.split("/")[-1]))
                    sys.stdout.flush()
                    time.sleep(0.1)
                    #except:
                        #error_list.append(f_path)
    #print("\nerrors? list of files not copied:")
    #for i in error_list:
    #    print("{}".format(i))
    print("\n{} files copied to {}".format(c, dest_dir))
