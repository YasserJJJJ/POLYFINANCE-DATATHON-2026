import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// En local, /api est redirigé vers l'API FastAPI (uvicorn sur le port 8000).
// En production, VITE_API_URL pointe vers l'API déployée sur AWS.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(path.dirname(fileURLToPath(import.meta.url)), './src') } },
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
})
