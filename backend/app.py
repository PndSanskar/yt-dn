import os
import glob
from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/info', methods=['POST'])
def get_info():
    """
    Fetch video information (title, thumbnail, duration) from a URL.
    """
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
        'quiet': True
    }

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
