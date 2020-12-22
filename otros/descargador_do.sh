
# descargador de archivos
# x: resoluciones
# el hasta es exclusivo

#  for x in {80000000..89999999};
#  do echo "x:$x";

#def
tribunal=260
x=80000000
hasta=89999999

#auto
#mkdir -p t$tribunal
# desde x hasta
while [ $x -lt $hasta ];
  do
    wget -O juicios/t$((tribunal))x$x.pdf "http://civil.poderjudicial.cl/CIVILPORWEB/DownloadFile.do?TIP_Documento=3&TIP_Archivo=3&COD_Opcion=1&COD_Tribunal=$tribunal&CRR_IdTramite=10000000&CRR_IdDocumento=$x";
  let x+=1;
done
# borrar vacios
find t$tribunal/. -type f -size 0 -delete
# contar los restantes
ls -l | wc -l
# borrar lista antigua
rm lista_res.txt
# nueva lista
ls juicios > lista_res.txt
