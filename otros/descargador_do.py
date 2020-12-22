

# bajador de las paginas del diario odicial
# información desde el 1 de enero hasta el 14 de diciembre de 2017
from datetime import datetime
import sh
import sys

#meses de 30 dias
meses_30 = (4, 6, 9, 11)

# domingo es 1 de enero
feriados = ((1,1),(2,1),(14,4),(15,4),(1,5),(7,6),(26,6),(15,8)\
,(18,9),(19,9),(9,10),(27,10),(1,11),(8,12),(25,12))

def cuenta_mes(dias, mes, domingo, numero):
    dia = 1
    for dias in range(dias):
        if domingo % 7 != 0 and (dia,mes) not in feriados:
            # wget webs
            url = "http://www.diariooficial.interior.gob.cl/edicionelectronica/empresas_cooperativas.php"
            edicion = "?date={:%d-%m-%Y}&edition={}".format(datetime(2017,mes,dia),numero)
            sys.stdout.write(edicion+"\n")
            url += edicion
            archivo = "--output-document=DO_ediciones/{}.txt".format(numero)
            sh.wget(archivo, "--user-agent=Mozilla", url)
            sys.stdout.write("ok\n")
            # leer CVEs
            CVEs = []
            with open("DO_ediciones/{}.txt".format(numero)) as f:
                for line in f:
                    if "CVE" in line and len(line.split()) > 6:
                        CVEs.append(line.split()[5][5:12])
            f.close()
            # wget PDFs
            for cve in CVEs:
                url_pdf = "http://www.diariooficial.interior.gob.cl/publicaciones/"
                cve_pdf = "{:%Y/%m/%d}/{}/05/{}.pdf".format(datetime(2017,mes,dia),numero,cve)
                sys.stdout.write(cve_pdf+"\n")
                url_pdf += cve_pdf
                archivo_pdf = "--output-document=DO_pdfs/{}_{}.pdf".format(numero,cve)
                sh.wget(archivo_pdf, "--user-agent=Mozilla", url_pdf)
                sys.stdout.write("ok\n")
            # nuevo ciclo
            sys.stdout.write("fin numero\n\n")
            numero += 1
        dia += 1
        domingo += 1
    mes += 1
    return domingo, numero

# 1er numero del 2017
numero = 41648
# 1 de enero fue domingo
domingo = 7
for mes in range(1,13):
    if mes in meses_30:
        domingo, numero = cuenta_mes(30, mes, domingo, numero)
    elif mes == 2:
        domingo, numero = cuenta_mes(28, mes, domingo, numero)
    else:
        domingo, numero = cuenta_mes(31, mes, domingo, numero)
