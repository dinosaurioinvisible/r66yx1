#!/bin/bash

# descargador de indices para descagador noticias de emol

# pagina_base = https://www.emol.com/sitemap/noticias/$anio/index.html
# console.log(page.plainText);

for anio in {2000..2018};
  do
    phantomjs --ssl-protocol=any --ignore-ssl-errors=true save_page.js "https://www.emol.com/sitemap/noticias/$anio/index.html" > emol/index_$anio.txt
  done
