import os
import glob
from flask import Flask, request, send_file, jsonify, after_this_request, send_from_directory
from flask_cors import CORS
import yt_dlp

# Serve the React app build folder
app = Flask(__name__, static_folder='client_build', static_url_path='')
CORS(app)

DOWNLOAD_FOLDER = '/tmp/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Helper to setup cookies from Env Var
def setup_cookies():
    cookie_content = os.environ.get('COOKIES_TXT_CONTENT')
    if cookie_content:
        with open('cookies.txt', 'w') as f:
            f.write(cookie_content)

setup_cookies()

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/')
def home():
    return "Backend is running! API is ready."


@app.route('/info', methods=['POST'])
def get_info():
    """
    Fetch video information (title, thumbnail, duration) from a URL.
    """
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Best attempt to avoid bot detection
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    # Check for cookies file to bypass restrictions
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

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
        error_msg = str(e)
        if "Sign in to confirm" in error_msg:
             return jsonify({'error': 'Server IP blocked by YouTube. Cookies required.'}), 403
        return jsonify({'error': error_msg}), 400


@app.route('/download', methods=['POST'])
def download():
    """
    Download the video, merge audio/video, and serve it to the client.
    Cleans up the file after request.
    """
    data = request.json
    url = data.get('url')

    # Clean up old files in tmp to prevent disk fill-up
    files = glob.glob(f'{DOWNLOAD_FOLDER}/*')
    for f in files:
        try:
            os.remove(f)
        except Exception:
            pass

    # yt-dlp options for best quality
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'noplaylist': True,  # Simple version handles single video
        'merge_output_format': 'mp4',
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # Fix extension if merge changed it (e.g. mkv -> mp4)
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                filename = f"{base}.mp4"

            @after_this_request
            def remove_file(response):
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                except Exception as error:
                    app.logger.error("Error removing downloaded file", error)
                return response

            return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
