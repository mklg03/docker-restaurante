FROM python:3.10-slim
WORKDIR /app
COPY admin.py .
RUN pip install --no-cache-dir requests ldap3
CMD ["python", "admin.py"]