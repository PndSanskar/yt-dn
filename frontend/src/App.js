import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

/**
 * Main Application Component
 * Handles URL input, fetching video info, and triggering downloads.
 */

// API_URL is empty because frontend and backend are now on the same origin
const API_URL = "";

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState(null);
  const [error, setError] = useState('');

  const fetchInfo = async () => {
    if (!url) return;
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
      <h1 style={{ color: '#333', marginTop: 0 }}>Convenience tools test by Pnd_Sanskar</h1>
      <p style={{ color: '#666', fontSize: '0.9rem' }}>Enter a YouTube URL below</p>

      <input
        type="text"
        placeholder="https://youtube.com/watch?v=..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <button onClick={fetchInfo} disabled={loading || !url}>
        {loading ? 'Processing...' : 'Get Info'}
      </button>

      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      {info && (
        <div className="preview">
          <img src={info.thumbnail} alt="thumb" />
          <h3 style={{ fontSize: '1.1rem' }}>{info.title}</h3>
          <p>{info.duration}</p>
          <button onClick={handleDownload} disabled={loading} style={{ backgroundColor: '#28a745' }}>
            {loading ? 'Downloading (this may take time)...' : 'Download High Quality MP4'}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
