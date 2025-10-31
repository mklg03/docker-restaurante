FROM python:3.10-slim

WORKDIR /app

COPY app.py .

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
 && pip install --no-cache-dir flask requests psycopg2-binary \
 && apt-get remove -y gcc \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

CMD ["python", "app.py"]
