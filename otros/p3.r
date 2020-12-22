

library(neuralnet)
View(datap3)

set.seed(111)
size.sample <- 50
p3train <- datap3[sample(1:nrow(datap3),size.sample),]
nnet_p3 <- p3train

# Binarize the categorical output
nnet_p3 <- cbind(nnet_p3, p3train$lugar == 'usach')
nnet_p3 <- cbind(nnet_p3, p3train$lugar == 'lascondes')
nnet_p3 <- cbind(nnet_p3, p3train$lugar == 'melipilla')

names(nnet_p3)[6] <- 'usach'
names(nnet_p3)[7] <- 'lascondes'
names(nnet_p3)[8] <- 'melipilla'

head(nnet_p3)

nnp3 <- neuralnet(usach+lascondes+melipilla ~
                    nitratos+sulfatos+amonio+cloruros,
                  data=nnet_p3,
                  hidden=c(9))

plot(nnp3)

mypredict <- compute(nnp3, datap3[-5])$net.result

maxidx <- function(arr) {
  return(which(arr == max(arr)))
}
idx <- apply(mypredict, c(1), maxidx)
prediction <- c('usach','lascondes', 'melipilla')[idx]
table(prediction, datap3$lugar)
