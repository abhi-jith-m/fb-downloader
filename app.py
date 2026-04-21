import yt_dlp
import os
import random
import string
from flask import Flask, render_template, request, jsonify, send_file, after_this_request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    platform = request.json.get('platform')
    video_format = request.json.get('videoFormat', 'mp4')
    audio_format = request.json.get('audioFormat', 'best')
    video_quality = request.json.get('videoQuality', 'best')

    if not video_url or not platform:
        return jsonify({'success': False, 'error': 'Missing URL or platform'}), 400

    try:
        unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # ✅ Only change: /tmp instead of static/videos
        video_filename = f"{platform}_{unique_id}.{video_format}"
        output_path = os.path.join('/tmp', video_filename)

        if video_quality != 'best':
            format_selection = f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]'
        else:
            format_selection = 'bestvideo+bestaudio/best'

        if audio_format != 'best' and video_format in ['mp3', 'aac', 'wav', 'm4a']:
            format_selection = f'bestaudio/{audio_format}'
            video_filename = f"{platform}_{unique_id}.{audio_format}"
            output_path = os.path.join('/tmp', video_filename)

        ydl_opts = {
            'format': format_selection,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': video_format,
        }

        if platform == 'instagram':
            cookie_file = './instagram_cookies.txt'
            if os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # yt-dlp sometimes changes the extension after merging, find the actual file
        actual_path = output_path
        if not os.path.exists(actual_path):
            for f in os.listdir('/tmp'):
                if unique_id in f:
                    actual_path = os.path.join('/tmp', f)
                    video_filename = f
                    break

        if not os.path.exists(actual_path):
            return jsonify({'success': False, 'error': 'File not found after download'}), 500

        @after_this_request
        def remove_file(response):
            try:
                os.remove(actual_path)
            except Exception:
                pass
            return response

        return send_file(actual_path, as_attachment=True, download_name=video_filename)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)