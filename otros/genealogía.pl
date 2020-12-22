
% casos conocidos de la relacion padre:
padre(juan,pedro).
padre(jose,pedro).
padre(maria,pedro).
padre(pedro,pablo).
padre(ana,alberto).

% casos conocidos de la relacion madre:
madre(juan,ana).
madre(jose,ana).
madre(maria,ana).
madre(pedro,juanita).
madre(ana,julia).

% reglas para la relacion abuelo_paterno(X,Y) "Y es abuelo_paterno de X":
abuelo_paterno(X,Y) :- padre(X,Z),padre(Z,Y).

% reglas para la relacion hijo(X,Y) "Y es hijo/a de X":
hijo(X,Y) :- padre(Y,X).
hijo(X,Y) :- madre(Y,X).

% reglas para la relacion descendiente(X,Y) "Y es descend. de X" (recursiva):
descendiente(X,Y) :- hijo(X,Y).
descendiente(X,Y) :- hijo(X,Z),descendiente(Z,Y).

% reglas para la relacion ancestro(X,Y) "Y es ancestro de X" (recursiva):
ancestro(X,Y) :- padre(X,Y).
ancestro(X,Y) :- madre(X,Y).
ancestro(X,Y) :- padre(X,Z),ancestro(Z,Y).
ancestro(X,Y) :- madre(X,Z),ancestro(Z,Y).
