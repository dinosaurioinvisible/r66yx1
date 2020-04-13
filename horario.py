
import numpy as np


# info
niveles = 12
cursos_por_nivel = [2,2,2,2,2,2,2,2,2,2,2,2]
# cargas
asig_1a4 = ["len", "mat", "his", "arte", "mus", "ef", "o", "tec", "rel", "ing", "cs", "ld"]
hh1 = [8, 6, 3, 2, 2, 4, 1, 1, 2, 0, 3, 6]
hh2 = [8, 6, 3, 2, 2, 4, 1, 1, 2, 0, 3, 6]
hh3 = [8, 6, 3, 2, 2, 4, 1, 1, 2, 0, 3, 6]
hh4 = [8, 6, 3, 2, 2, 4, 1, 1, 2, 0, 3, 6]
cargas_por_nivel = [zip(asig_1a4, hh1), zip(asig_1a4, hh2), zip(asig_1a4, hh3), zip(asig_1a4, hh4)]
asig_5y6 = ["len", "mat", "his", "arte", "mus", "ef", "o", "tec", "rel", "ing", "cs", "ld"]
hh5 = [6, 6, 4, 2, 2, 2, 1, 1, 2, 3, 4, 5]
hh6 = [6, 6, 4, 2, 2, 2, 1, 1, 2, 3, 4, 5]
cargas_por_nivel.extend([zip(asig_5y6, hh5), zip(asig_5y6, hh6)])
asig_7y8 = ["len", "mat", "his", "arte", "mus", "ef", "o", "tec", "rel", "ing", "cs", "ld"]
hh7 = [6, 6, 4, 3, 0, 2, 1, 1, 2, 3, 4, 6]
hh8 = [6, 6, 4, 3, 0, 2, 1, 1, 2, 3, 4, 6]
cargas_por_nivel.extend([zip(asig_7y8, hh7), zip(asig_7y8, hh8)])
asig_IyII = ["len", "mat", "his", "arte", "mus", "ef", "o", "tec", "rel", "ing", "cs", "ld"]
hhI = [6, 7, 4, 2, 0, 2, 1, 2, 2, 4, 6, 6]
hhII = [6, 7, 4, 2, 0, 2, 1, 2, 2, 4, 6, 6]
cargas_por_nivel.extend([zip(asig_IyII, hhI), zip(asig_IyII, hhII)])
asig_IIIyIV = ["len", "mat", "his", "arte", "mus", "ef", "o", "rel", "ing", "bio", "quim", "fis", "fil", "dlen", "dhis", "dfil", "dmat", "dbio", "dquim", "dfis"]
hhIII_H = [3, 3, 4, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 3, 3, 3, 0, 0, 0, 0]
hhIII_C = [3, 3, 4, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 0, 0, 0, 3, 2, 2, 2]
hhIV_H = [3, 3, 4, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 3, 3, 3, 0, 0, 0, 0]
hhIV_C = [3, 3, 4, 2, 0, 2, 1, 2, 3, 2, 2, 0, 3, 0, 0, 0, 3, 2, 2, 2]
cargas_por_nivel.extend([zip(asig_IIIyIV, hhIII_H), zip(asig_IIIyIV, hhIII_C), zip(asig_IIIyIV, hhIV_H), zip(asig_IIIyIV, hhIV_C)])
# horas de clases (NO incluye hora de almuerzo aun)
horas_por_nivel = []
horas_12 = [8,8,8,8,6]
almuerzo_12 = 6
horas_por_nivel.extend([horas12, almuerzo_12])
horas_34 = [8,8,8,8,6]
almuerzo_34 = 7
horas_56 = [8,8,8,8,6]
almuerzo_56 = 7
horas_78 = [8,8,8,8,6]
almuerzo_78 = 7
horas_por_nivel.extend([horas34, almuerzo_34], [horas56, almuerzo_56], [horas78, almuerzo_78])
horas_m1 = [8,8,8,8,6]
almuerzo_78 = 8
horas_m2 = [8,8,8,8,6]
almuerzo_78 = 8
horas_por_nivel.extend([horasm1, almuerzo_m1], [horasm2, almuerzo_m2])


class Curso:
    def __init__(self, nombre=None\
    , carga=[], horario=[]):
        self.nombre = nombre
        self.carga = carga
        self.horario = horario

class Profesor:
    def __init__(self, nombre=None\
    , disponibilidad=[], horario=[]):
        self.nombre = nombre
        self.disp = disponibilidad
        self.horario = horario

class Organizador:
    def __init__(self, niveles=12\
    , cursos_por_nivel=[]\
    , cargas_por_nivel=[]\
    , horas_por_nivel=[]):
        self.niveles = niveles
        self.cursos_por_nivel = cursos_por_nivel
        self.cargas_por_nivel = cargas_por_nivel
        self.horas_por_nivel = horas_diarias
        # internas
        self.cursos = {}
        self.profesores = {}
        self.crear_cursos()
        self.crear_profesores()

    def crear_cursos(self):
        # diccionario nombre:curso
        # cursos["3b"] = objecto<curso>
            # objeto curso
            # curso.nombre = "3b"
            # curso.carga: diccionario asignaturas:horas
                # carga["mat"] = 6
                # > cursos["3b"].carga["mat"] = 6
            # curso.horario: matriz de espacios vacios por dia
                # horario[0][:3]: [None, None, None] (lunes, primeras 3 horas)
                # > cursos["3b"].horario
        for i in range(self.niveles):
            for j in range(self.cursos_por_nivel[i]):
                # nombre del curso
                letra = "a" if j == 0 else "b"
                nombre = str(i+1)+letra
                # carga horaria (zip)
                carga = {}
                for asig in self.cargas_por_nivel[i]:
                    carga[asig[0]] = asig[1]
                # horario vacio
                horario = []
                for dia in self.horas_por_nivel[i]:
                    horas_dia = [None]*dia[0]
                    horas_dia.insert(dia[1], "X")
                    horario.append(horas_dia)
                # crear curso
                curso = Curso(nombre, carga, horario)
                # agregar al conjunto de cursos
                self.cursos[nombre] = curso

    def crear_profesores(self):
        # diccionario nombre:profesor
        for i in range(self.)















#
