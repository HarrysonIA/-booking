# Usa la imagen oficial de Python como base
FROM python:latest

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
COPY requirements.txt requirements.txt

# Instala las dependencias del proyecto
RUN pip install -r requirements.txt
    
# Copia el contenido de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto 5000 para que la aplicación Flask pueda ser accesible desde el exterior
EXPOSE 5000

# Define el comando por defecto para ejecutar la aplicación
# Reemplaza CMD ["python", "run.py"] con
CMD ["python", "main.py"]

