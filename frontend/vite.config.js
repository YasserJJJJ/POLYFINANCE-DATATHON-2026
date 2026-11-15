import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En local, /api est redirigé vers l'API FastAPI (uvicorn sur le port 8000).
// En production, VITE_API_URL pointe vers l'API déployée sur AWS.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
})
