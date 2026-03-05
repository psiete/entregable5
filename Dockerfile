# Usar imagen base oficial de Python slim para reducir tamaño
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos al contenedor
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación y tests al contenedor
COPY *.py .

# Exponer el puerto 8000 (puerto estándar para FastAPI)
EXPOSE 8000

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Comando para ejecutar la aplicación FastAPI con uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
