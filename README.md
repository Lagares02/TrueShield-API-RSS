# API News
API de gestion de noticias por medio de RSS 

## Diagrama ER

<img src="D:\Users\Windows 10\Documents\TrueShield\TrueShield-API-RSS\imgs\Diagrama_ER .png" alt="Diagrama ER" />

Los nombres de las tablas tienen el `main_` antes del nombre del modelo, todo en minuscula, por ejemplo las tablas del diagrama son:

    - `main_media`
    - `main_new`
    - `main_rss_url`


## Requerimientos 

- ***Obtencion de noticias:*** Se obtienen las noticias de las RSS y se guardan en la tabla de news.
- ***Obtencion de noticias por filtro:*** Busca e imprime noticias por categoria.