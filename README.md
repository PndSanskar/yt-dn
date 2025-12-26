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

This project includes a `render.yaml` file (Render Blueprint) for easy deployment:

1. Push this entire repository to GitHub.
2. Go to your **Render Dashboard**.
3. Click **Blueprints** > **New Blueprint Instance**.
4. Connect this repository.
5. Render will automatically detect the configuration and deploy the Python API via Docker.

Alternatively, you can manually create a Web Service, set the runtime to **Docker**, and point the **Docker Context** to the `backend` folder.

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
