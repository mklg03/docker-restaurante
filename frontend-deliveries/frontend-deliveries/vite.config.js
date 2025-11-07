import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // necesario para exponer desde Docker
    port: 3000,
    proxy: {
      '/deliveries': {
        target: 'http://host.docker.internal:8081', // redirige al backend en tu máquina
        changeOrigin: true,
        secure: false,
      },
    },
  },
});