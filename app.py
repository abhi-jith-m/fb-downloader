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
        is_audio_only = video_format in ['mp3', 'aac', 'wav', 'm4a']

        ext = audio_format if (is_audio_only and audio_format != 'best') else video_format
        video_filename = f"{platform}_{unique_id}.{ext}"
        output_path = os.path.join('/tmp', video_filename)

        # ✅ Always use pre-merged 'best' — no ffmpeg needed
        if is_audio_only:
            format_selection = 'bestaudio/best'
        elif video_quality != 'best':
            format_selection = f'best[height<={video_quality}]/best'
        else:
            format_selection = 'best'

        ydl_opts = {
            'format': format_selection,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            # ❌ Removed merge_output_format — nothing to merge
        }

        if platform == 'instagram':
            cookie_file = './instagram_cookies.txt'
            if os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # yt-dlp may change extension after download, find actual file
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