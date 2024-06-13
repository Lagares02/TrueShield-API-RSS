# Api News
Api de gestion de noticias por medio de RSS 

## Diagrama ER

![demo](/imgs/Diagrama_ER.png)

Los nombres de las tablas tienen el `main_` antes del nombre del modelo todo en minuscula por ejemplo las tablas del diagrama serian :

    - `main_media`
    - `main_new`
    - `main_rss_url`


## Requerimientos
- ***Obtencion de noticias:*** obten las noticias de los RSS y guardalas en la tabla news.
- ***Obtencion de noticias por filtro:*** busca noticias por categoria, medio de comunicacion  o fecha de publicion.
- ***Eliminacion de noticias antoguas:*** elimina las noticas con por lo menos 3 meses de antiguedad en su fecha de publicacion 