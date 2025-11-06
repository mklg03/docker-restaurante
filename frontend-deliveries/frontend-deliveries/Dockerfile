# Etapa base
FROM node:22-alpine

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias y código
COPY package*.json ./
RUN npm install

COPY . .

# Exponer el puerto de desarrollo de Vite
EXPOSE 3000

# Comando para iniciar en modo desarrollo
CMD ["npm", "run", "dev"]