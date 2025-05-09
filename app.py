import yt_dlp
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'static/videos/videoplayback.mp4',  # Always save as 'videoplayback.mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return jsonify({'success': True, 'filename': 'videoplayback.mp4'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/videos', exist_ok=True)
    app.run(debug=True)
