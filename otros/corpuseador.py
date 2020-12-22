
import sys
import os
import re
from tqdm import tqdm
from collections import defaultdict

# ruta a los archivos desde el directorio de trabajo
data_dir = "sonda/wget_plp"
dir_path = os.path.join(os.getcwd(), data_dir)

def crear_corpus(data_path=dir_path):
    enunciados = []

    # abrir y guardar enunciados
    for file in os.listdir(data_path):
        if "html" in file:
            print("\n"+file)
            with open(os.path.join(data_path, file)) as data:
                enunciados += [line for line in tqdm(data) if "<p>" in line]

    # hacer corpus
    corpus = []
    formatos = defaultdict(int)
    for enunciado in enunciados:
        # limpiar <p> y </p> y reemplazar html &quots;
        enunciado = re.sub(".quot;", "\"", enunciado)
        enunciado = re.sub("<.?p>", "", enunciado)
        try:
            # clasificar segun formato
            if "<" in enunciado.split()[0]:
                formato = re.sub(">.*", "", enunciado.split()[0][1:])
                formato = re.sub(".*<", "", formato)
            else:
                formato = "texto"
            formatos[formato] += 1
        except:
            pass
        # limpiar el resto
        enunciado = re.sub("<.*>\\n", "", enunciado)
        # corpus
        corpus.append(enunciado)
    print("\nformatos:\n")
    [print("{} : {}".format(x, formatos[x])) for x in formatos]
    #[sys.stdout.write("{} : {}\n".format(x, formatos[x])) for x in formatos]

    # estadisticas
    types = defaultdict(int)
    for enunciado in corpus:
        for token in enunciado.split():
            types[token] += 1
    num_types = len(types)
    num_tokens = sum([types[ocurrencias] for ocurrencias in types])
    num_enunciados = len(corpus)
    print("\n")
    print("enunciados: {}".format(num_enunciados))
    print("types: {}".format(num_types))
    print("tokens: {}".format(num_tokens))
    print("\n")

    # escribir a un .txt
    f = open("corpus.txt", "w")
    for x in tqdm(corpus):
        f.write("{}\n".format(x))
    f.close()

    return corpus

if __name__ == "__main__":
    crear_corpus()
