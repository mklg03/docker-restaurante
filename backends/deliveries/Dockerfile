FROM python:3.10-slim

WORKDIR /app


COPY requirements.txt ./


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get remove -y gcc \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*


COPY app.py ./

EXPOSE 5000
CMD ["python", "app.py"]