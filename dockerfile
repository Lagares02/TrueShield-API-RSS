# Usa la imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias especificadas en requirements.txt
RUN pip3 install -r requirements.txt

# Copia el resto de los archivos al directorio de trabajo
COPY . .

# Expone el puerto 8001 para que la aplicación sea accesible desde fuera del contenedor
EXPOSE 8001

# Comando para ejecutar la aplicación cuando se inicie el contenedor
CMD ["python3", "main.py"]