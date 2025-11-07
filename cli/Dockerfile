FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    libldap2-dev libsasl2-dev gcc && \
    pip install ldap3 requests && \
    apt-get clean

# Copiar CLI único
COPY cli.py /app/cli.py

ENTRYPOINT ["python", "cli.py"]
