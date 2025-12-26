# Seamless YouTube Downloader

A full-stack application to download high-quality YouTube videos (up to 4K) and playlists using `yt-dlp` and `FFmpeg`.

## Architecture

- **Frontend:** React.js
- **Backend:** Python Flask
- **Core Logic:** `yt-dlp` for stream fetching, `ffmpeg` for merging video/audio.
- **Deployment:** Docker (Backend), GitHub Pages (Frontend).

## Prerequisites

- Node.js & npm
- Python 3.9+
- FFmpeg (installed and in system PATH for local development)

## Local Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
   The backend will start on `http://0.0.0.0:10000`.

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`.

## Deployment

### Backend (Render)

1. Push the `backend` folder (or this entire repo, pointing to the backend folder) to GitHub.
2. Create a new Web Service on Render.
3. Select **Docker** as the runtime.
4. Deploy and copy the provided URL.

### Frontend (GitHub Pages)

1. Update `frontend/src/App.js`: Replace `YOUR-RENDER-APP-NAME` with your actual Render backend URL.
2. Update `frontend/package.json`: Add `"homepage": "https://<your-github-username>.github.io/<repo-name>"`
3. Deploy:
   ```bash
   cd frontend
   npm run deploy
   ```

## License

[MIT](LICENSE)
