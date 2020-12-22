#!/bin/bash

# descargador de noticias del mercurio
# pagina base: https://www.emol.com/sitemap/noticias/2018/emol_noticias_$anio_$mes_$noticia.html
# console.log(page.content);

for mes in $(seq -w 1 12);
  do
    for partes in $(seq -w 1 20);
    do
      x="$anio"_"$mes"_00000"$partes"
      phantomjs --ssl-protocol=any --ignore-ssl-errors=true save_page.js "https://www.emol.com/sitemap/noticias/$anio/emol_noticias_$x.html" > emol/emol_$x.txt
    done
  done
