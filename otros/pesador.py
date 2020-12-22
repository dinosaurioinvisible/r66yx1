#!/usr/bin/env python

# buscador de pesos dentro del computador

import os
from tqdm import tqdm
from operator import itemgetter
from collections import defaultdict


def sonda(rootdir="/Users/r66y", activate_return=0, print_path=1):
    print("\n")
    lista = []
    dir2 = []
    dir3 = []
    # pesos archivos
    for roots, dirs, files in tqdm(os.walk(rootdir)):
        for file in files:
            path = os.path.join(roots, file)
            try:
                peso = round((os.stat(path).st_size/1000000),2)
            except:
                peso = 0
            lista.append([file, peso, path])
            dir2.append([peso, path.split("/")[3]])
            try:
                dir3.append([peso, path.split("/")[3]+"/"+path.split("/")[4]])
            except:
                pass
    lista.sort(reverse=True, key=itemgetter(1))
    # pesos carpetas
    print("\n"+"..."+"\n")
    # nivel 2
    pesos_dir2 = defaultdict(float)
    for x in dir2:
        pesos_dir2[x[1]] += x[0]
    lista_dir2 = [[key, round((pesos_dir2[key]/1000),2)] for key in pesos_dir2.keys()]
    lista_dir2.sort(reverse=True, key=itemgetter(1))
    # nivel 3
    pesos_dir3 = defaultdict(float)
    for x in dir3:
        pesos_dir3[x[1]] += x[0]
    lista_dir3 = [[key, round((pesos_dir3[key]/1000),2)] for key in pesos_dir3.keys()]
    lista_dir3.sort(reverse=True, key=itemgetter(1))
    # output
    print("\n"+"..."+"\n")
    f = open("pesos.csv", "w")
    if print_path == 1:
        for i in tqdm(range(len(lista))):
            if lista[i][1] >= 100:
                # indice - nombre - peso - direccion
                # f.write("\n\n{} - {}, {} Mb\n\t{}\n\n".format(str(i+1), lista[i][0], str(lista[i][1]), str(lista[i][2])))
                f.write("\n{};{};{};{}".format(str(i+1), lista[i][0], str(lista[i][1]), str(lista[i][2])))
        # dirs
        f.write("\n\n\n")
        for i in tqdm(range(len(lista_dir2))):
            if lista_dir2[i][1] >= 0:
                f.write("\n{};{};{}".format(str(i+1), lista_dir2[i][0], str(lista_dir2[i][1])))
        f.write("\n\n\n")
        for i in tqdm(range(len(lista_dir3))):
            if lista_dir3[i][1] >= 0:
                f.write("\n{};{};{}".format(str(i+1), lista_dir3[i][0], str(lista_dir3[i][1])))
    else:
        for i in tqdm(range(len(lista))):
            f.write("\n\n{} - {}, {} Mb\n".format(str(i+1), lista[i][0], str(lista[i][1]), str(lista[i][2])))
    f.close()
    if activate_return == 1:
        return lista
    else:
        print("\n"+"...ok"+"\n")

if __name__ == "__main__":
    sonda()
