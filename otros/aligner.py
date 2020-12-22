
import re
from tqdm import tqdm

def align(inukfile, f_inukfile, engfile):
    with open(inukfile) as f1:
        inuk_copy = [line for line in f1]
    with open(inukfile) as f1:
        inuk = [re.sub(' ', "", line) for line in f1]
    with open(f_inukfile) as f2:
        f_inuk_copy = [line for line in f2]
    with open(f_inukfile) as f2:
        f_inuk = [re.sub(' ', "", line) for line in f2]
    with open(engfile) as f3:
        eng = [line for line in f3]
        #eng = [re.sub(' ', "", line) for line in f3]
    lines = 100000
    #aligned_inuk = []
    #aligned_eng = []
    aligned = []
    non_aligned = []
    a = 0
    problem = False
    for i in tqdm(range(lines)):
        if problem == True:
            while inuk[i] != f_inuk[i+a]:
                a += 1
            print("realigned")
            problem = False

        if inuk[i] == f_inuk[i+a]:
            aligned.append((inuk_copy[i], f_inuk_copy[i+a], eng[i]))
        else:
            print("non aligned at line: "+str(i))
            non_aligned.append((i, inuk[i], f_inuk[i], eng[i]))
            problem = True

    with open("aligned_bpe_inuk", "w") as f:
        for line in aligned:
            f.write(line[1])
    with open("aligned_eng", "w") as f:
        for line in aligned:
            f.write(line[2])

    return aligned, non_aligned
