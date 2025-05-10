import yt_dlp
import os
import random
import string
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    platform = request.json.get('platform')

    if not video_url or not platform:
        return jsonify({'error': 'Missing URL or platform'}), 400

    try:
        # Generate unique random filename
        unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        video_filename = f"videoplayback_{unique_id}.mp4"
        output_path = os.path.join('static', 'videos', video_filename)

        ydl_opts = {
             'format': 'best',
            'outtmpl': output_path,
            'cookiefile': 'instagram_cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return jsonify({'success': True, 'filename': video_filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/videos', exist_ok=True)
    app.run(debug=True)