#!/usr/bin/env python
# -*- coding: utf-8 -*

# indexador para noticias de emol

import os
#import subprocess
from collections import defaultdict
from tqdm import tqdm
import re

# parametros
inicio = 2018
fin = 2019
save_path = ""
save_dir = "emol"

# descargar las paginas con los indices
# bash > phantomjs
def descargador_de_indices(inicio=inicio, fin=fin, save_path=save_path, save_dir=save_dir):
    if os.path.isdir(save_path) == False:
        save_path = os.path.join(os.getcwd(), save_dir)
        print("directory not found, saving to: {}".format(save_path))
    for anio in range(inicio, fin+1):
        url = "https://www.emol.com/sitemap/noticias/{}/index.html".format(anio)
        save_path_anio = os.path.join(save_path, "index_{}.txt".format(anio))
        bash_command = "phantomjs --ssl-protocol=any --ignore-ssl-errors=true save_page.js {} > {}".format(url, save_path_anio)
        # bash > phantomjs
        os.system(bash_command)
        #subprocess.Popen(bash_command.split())


# abrir y leer paginas-indices y construir indice.txt
# python
def indexador(save_dir=save_dir):
    # para contar desde el mes hasta el siguiente
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio"\
    , "agosto", "septiembre", "octubre", "noviembre", "diciembre", "fin"]
    # todos los indices
    indices = {}
    for file in os.listdir(save_dir):
        # descartar otros archivos
        if os.path.basename(file).split("_")[0] == "index":
            # solo los numeros para el año
            name = "".join([x for x in os.path.basename(file) if x.isdigit()])
            # contador de meses
            i = 0
            # contador de paginas de noticias
            c = 0
            # indices del archivo
            indice = []
            file_path = os.path.join(save_dir, file)
            with open(file_path) as f:
                for line in f:
                    if meses[0] in line.lower():
                        c = 0
                        i += 1
                    elif meses[i] in line.lower():
                        indice.append(c)
                        c = 0
                        i += 1
                    elif "mercurio" in line.lower():
                        indice.append(c)
                        break
                    else:
                        c += 1
            indices[name] = indice
    return indices


# descargar los nombres de las paginas
# bash > wget (mas rapido que phantomjs)
def descargar_partes(indices, inicio=inicio, fin=fin, save_path=save_path, save_dir=save_dir):
    if os.path.isdir(save_path) == False:
        save_path = os.path.join(os.getcwd(), save_dir)
        print("directory not found, saving to: {}".format(save_path))
    for anio in range(inicio,fin+1):
        for mes in range(12):
            partes = indices[str(anio)][mes]
            for parte in range(partes):
                # partes es de 2 digitos
                x = "{}_{:02d}_00000{:02d}".format(anio, mes+1, parte+1)
                url = "https://www.emol.com/sitemap/noticias/{}/emol_noticias_{}.html".format(anio, x)
                save_path_x = "{}/parte_{}.txt".format(save_path, x)
                # revisar si el archivo ya existe
                if os.path.isfile(save_path_x) == True:
                    pass
                else:
                    #bash_command = "phantomjs --ssl-protocol=any --ignore-ssl-errors=true save_page.js {} > {}".format(url ,save_path)
                    bash_command = "wget -O {} {} --no-check-certificate".format(save_path_x, url)
                    # python > bash
                    os.system(bash_command)
                    #subprocess.Popen(bash_command.split())


# crear lista de paginas para descargar
# python
def limpiador(save_dir=save_dir, write=False):
    noticias = []
    for file in os.listdir(save_dir):
        if os.path.basename(file).split("_")[0] == "parte":
            file_path = os.path.join(save_dir, file)
            with open(file_path) as f:
                for line in f:
                    if "<li><a href=" in line:
                        noticia = line.split("\"")[1]
                        noticias.append(noticia)
                        print(noticia)
        print("\ntotal noticias: {}\n".format(len(noticias)))
    if write == True:
        save_path = os.path.join(save_dir, "_indice_noticias_emol.txt")
        file = open(save_path, "w")
        for enlace_noticia in noticias:
            file.write(enlace_noticia+"\n")
        file.close()
    return noticias


# descargar las paginas segun la lista
# bash > phantomjs
innot = "emol/_indice_noticias_emol.txt"
def descargador_de_paginas(indice_noticias=innot, save_path=save_path, save_dir="noticias"):
    if os.path.isdir(save_path) == False:
        save_path = os.path.join(os.getcwd(), save_dir)
    if os.path.isfile(indice_noticias) == False:
        raise("no index file")
    with open(indice_noticias) as f:
        for url in f:
            x = url.split("/")
            save_file = os.path.join(save_path, "{}{}{}_{}_{}_{}.txt".format(x[5],x[6],x[7],x[4],x[8],x[9]))
            bash_command = "phantomjs --ssl-protocol=any --ignore-ssl-errors=true save_page.js {} > {}".format(url, save_file)
            # bash > phantomjs
            os.system(bash_command)


# abrir, filtrar las paginas y contruir:
# a) corpus crudo (objeto)
# b) diccionario > (tema, usuario) : comentario
