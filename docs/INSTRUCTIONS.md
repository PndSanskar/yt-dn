# MASTER INSTRUCTION: Build Seamless YouTube Downloader Project

I want you to generate a full-stack project for a "Seamless YouTube Downloader" that supports high-quality video (up to 4K) and playlists using `yt-dlp` and `FFmpeg`.

## PROJECT ARCHITECTURE
1. **Frontend:** React.js (hosted on GitHub Pages).
2. **Backend:** Python Flask (hosted on Render via Docker).
3. **Core Logic:** The backend uses `yt-dlp` to fetch streams and `ffmpeg` to merge high-quality video+audio.

---

## STEP 1: BACKEND GENERATION (Folder: /backend)

Create a folder named `backend` and generate the following 4 files inside it.

### File 1: `backend/requirements.txt`
flask
flask-cors
yt-dlp
gunicorn

### File 2: `backend/Dockerfile`
(Note: We use Docker to ensure FFmpeg is installed on Render)
FROM python:3.9-slim

# Install system dependencies (FFmpeg is critical for merging streams)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Run the application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:10000", "--timeout", "120", "app:app"]

### File 3: `backend/render.yaml`
services:
  - type: web
    name: youtube-downloader-api
    env: docker
    plan: free
    autoDeploy: false

### File 4: `backend/app.py`
import os
from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp
import glob

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    ydl_opts = {'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration_string'),
                'is_playlist': 'entries' in info
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    
    # Clean up old files in tmp
    files = glob.glob(f'{DOWNLOAD_FOLDER}/*')
    for f in files:
        try:
            os.remove(f)
        except:
            pass

    # yt-dlp options for best quality
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'noplaylist': True, # Simple version handles single video
        'merge_output_format': 'mp4',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Fix extension if merge changed it
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                filename = f"{base}.mp4"

            @after_this_request
            def remove_file(response):
                try:
                    os.remove(filename)
                except Exception as error:
                    app.logger.error("Error removing or closing downloaded file handle", error)
                return response

            return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

---

## STEP 2: FRONTEND GENERATION (Folder: /frontend)

Create a folder named `frontend`. Assume `create-react-app` structure. Generate/Update the following files.

### File 1: `frontend/package.json` (Dependencies section only)
"dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
},
"scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
},
"devDependencies": {
    "gh-pages": "^6.1.0"
}

### File 2: `frontend/src/App.css`
body {
  background-color: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

input {
  width: 100%;
  padding: 12px;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #ff0000;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

button:disabled {
  background-color: #ccc;
}

button:hover:not(:disabled) {
  background-color: #cc0000;
}

.preview {
  margin-top: 1.5rem;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.preview img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 1rem;
}

### File 3: `frontend/src/App.js`
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// TODO: User must replace this with their actual Render URL after deployment
const API_URL = process.env.REACT_APP_API_URL || "https://YOUR-RENDER-APP-NAME.onrender.com";

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState(null);
  const [error, setError] = useState('');

  const fetchInfo = async () => {
    if(!url) return;
    setLoading(true);
    setError('');
    setInfo(null);
    try {
      const res = await axios.post(`${API_URL}/info`, { url });
      setInfo(res.data);
    } catch (err) {
      setError("Could not fetch video info. Check URL or Backend status.");
    }
    setLoading(false);
  };

  const handleDownload = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/download`, { url }, {
        responseType: 'blob'
      });
      
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `${info.title}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Download failed. Video might be too long for free tier timeout.");
    }
    setLoading(false);
  };

  return (
    <div className="card">
      <h1 style={{color: '#333', marginTop: 0}}>Video Downloader</h1>
      <p style={{color: '#666', fontSize: '0.9rem'}}>Enter a YouTube URL below</p>
      
      <input 
        type="text" 
        placeholder="https://youtube.com/watch?v=..." 
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      
      <button onClick={fetchInfo} disabled={loading || !url}>
        {loading ? 'Processing...' : 'Get Info'}
      </button>

      {error && <p style={{color: 'red', marginTop: '1rem'}}>{error}</p>}

      {info && (
        <div className="preview">
          <img src={info.thumbnail} alt="thumb" />
          <h3 style={{fontSize: '1.1rem'}}>{info.title}</h3>
          <p>{info.duration}</p>
          <button onClick={handleDownload} disabled={loading} style={{backgroundColor: '#28a745'}}>
            {loading ? 'Downloading (this may take time)...' : 'Download High Quality MP4'}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;

---

## STEP 3: DEPLOYMENT INSTRUCTIONS

1. **Backend (Render):**
   - Push the `/backend` folder to a GitHub Repo.
   - Go to Render Dashboard > New Web Service.
   - Connect Repo.
   - Runtime: **Docker**.
   - Deploy.
   - Copy the provided URL.

2. **Frontend (GitHub Pages):**
   - In `frontend/src/App.js`, replace `YOUR-RENDER-APP-NAME` with the URL from step 1.
   - In `frontend/package.json`, add `"homepage": "https://<your-github-username>.github.io/<repo-name>"`
   - Run `npm install`.
   - Run `npm run deploy`.