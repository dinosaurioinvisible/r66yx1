
# árboles de decisión interrelacionados

library(tree)

View(data02)

#gráfico completo
plot(data02,col=as.integer(data02$politica)+1)

#árbol basado en la categoría "ciencia"
p2 <- tree(ciencia ~., data02)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría "ateísmo"
p2 <- tree(ateismo ~., data02)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría "reciclaje"
p2 <- tree(reciclaje ~., data01)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en "nvecon" (estatus económico)
p2 <- tree(nvecon ~., data01)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría de tendencias politica
p2 <- tree(politica ~., data01)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría referente a la asistencia a misa
p2 <- tree(misa ~., data01)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría "trabajo"
p2 <- tree(trabajo ~., data01)
p2
summary(p2)
plot(p2);  text(p2)

#árbol basado en la categoría "ambientalismo"
p2 <- tree(ambientalismo ~., data01)
p2
summary(p2)
plot(p2);  text(p2)



