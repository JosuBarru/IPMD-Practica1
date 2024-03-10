# Utiliza la imagen base de Python 3
FROM python:3

# Establece el directorio de trabajo dentro del contenedor en /app
WORKDIR /app

# Copia el archivo main.py dentro del contenedor en /app
COPY main.py /app/

# Copia el archivo requirements.txt dentro del contenedor en /app
COPY requirements.txt /app/

# Instala las dependencias definidas en requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expone el puerto 80 para permitir la comunicación con el exterior
EXPOSE 80

# Comando para ejecutar la aplicación usando Gunicorn, sirviendo en todas las interfaces en el puerto 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]

