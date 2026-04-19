# Jyotisha Engine

A completely completely modernized, production-ready Vedic Astrology web application.
The backend relies on FastAPI and Swiss Ephemeris (`pyswisseph`) for highly accurate astronomical calculations, and the frontend is built with React/Vite using a custom "Ancient & Modern" UI library.

## Quick Start — Local Development

### 1. Start the Backend (FastAPI)
Open a terminal in this root directory (`Astro files`):
```bash
# 1. Activate your python 3.11 virtual environment
.\venv311\Scripts\activate

# 2. Start the server (runs on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```
✅ You can test the API by navigating to `http://localhost:8000/docs`

### 2. Start the Frontend (React + Vite)
Open a **second**, separate terminal, also in this root directory:
```bash
# 1. Move into the frontend directory
cd frontend

# 2. Install Node dependencies (only needed the first time)
npm install

# 3. Start the dev server (runs on http://localhost:5173)
npm run dev
```
✅ Open `http://localhost:5173` in your browser. The UI will automatically proxy API calls to your local backend.

---

## Deploying

### Deploying the Backend (Render.com)
The root folder is configured with `render.yaml` to easily deploy your backend as a Web Service.
1. Push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com).
3. Connect your GitHub repository.
4. Render will detect `render.yaml` and deploy your FastAPI application automatically.
5. Once deployed, note your URL (e.g. `https://jyotisha-engine.onrender.com`).

### Deploying the Frontend (GitHub Pages)

1. Open `frontend/.env.production` and replace `VITE_API_URL` with your new Render backend URL.
   ```env
   VITE_API_URL=https://your-app.onrender.com/api
   ```
2. If your repository name is not `<username>.github.io`, open `frontend/vite.config.js` and add your repo name as the base path:
   ```javascript
   export default defineConfig({
     base: '/repository-name/', 
     // ...
   })
   ```
3. Open a terminal and build the project:
   ```bash
   cd frontend
   npm run build
   ```
   *Note: If you get a Windows `rolldown/binding` error, simply delete `node_modules` and `package-lock.json` and run `npm install` again.*

4. After building, a `dist/` folder will be generated. You can deploy this directory to GitHub Pages using the `gh-pages` CLI:
   ```bash
   npx gh-pages -d dist
   ```
   *(Or simply go to your GitHub repository -> Settings -> Pages -> Deploy from Branch -> Select the branch you just pushed to).*
