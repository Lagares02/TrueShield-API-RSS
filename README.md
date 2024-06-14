# API News

## Introducción de la API

Esta API permite la gestión y consulta de noticias a través de diferentes categorías obtenidas mediante RSS La API está desarrollada con **FastAPI** y utiliza `SQLAlchemy` para la gestión de la base de datos **PostgreSQL**.

## Diagrama de arquitectura

Imagen.jpg

## Diagrama de clases

Imagen.jpg

## ¿Cómo está dividida la API?

### Estructura del proyecto

- `templates/`
	- `index.html` - Archivo **HTML** para la interfaz de usuario. 
- `main.py` - Archivo principal de la API donde se definen las rutas y la lógica principal.
- `requirements.txt` - Archivo con las librerías y paquetes necesarios

### Componentes

`main.py`: Contiene la configuración principal de **FastAPI**, las rutas para manejar las solicitudes, y la lógica para interactuar con la base de datos.

**Rutas principales:**
-   `/`: Renderiza el `index.html`.
-   `/validate_prompt`: Valida si un titular dado existe en la base de datos.
-   `/save_news`: Guarda las noticias obtenidas de los RSS en la base de datos (más específicamente en la tabla News).
-   `/news_by_category`: Obtiene todas las noticias clasificadas por categoría y las devuelve en formato JSON.

`templates/index.html`: Proporciona la interfaz de usuario para buscar y validar titulares de noticias, así como para guardar nuevas noticias.

## Ejecutemos la API

### Iniciamos un entorno virtual (Opcional)

-   Abre una terminal y navega al directorio del proyecto.
-   Crea el entorno:

> python -m venv venv 

- Activa el entorno creado (Para Windows):

> .\venv\Scripts\activate

### Instalamos los requerimientos

-   Cuando tengas el entorno virtual activado, puedes instalar las dependencias necesarias:

> pip install -r requirements.txt

### Clonar y ejecutar

- Clonamos el repo:

> git clone https://github.com/Lagares02/TrueShield-API-RSS.git

- Configura tus variables de entorno para la conexión de la base de datos
- Iniciamos el servidor con tan solo:

> py main.py

- Abre tu navegador y navega a `http://127.0.0.1:8001` para ver la interfaz de usuario.