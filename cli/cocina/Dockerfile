FROM python:3.10-slim

WORKDIR /app

# Copia el script correcto
COPY cocina.py .

RUN pip install --no-cache-dir requests ldap3

# CMD por defecto para ejecutar el script si quieres
CMD ["python", "cocina.py"]
