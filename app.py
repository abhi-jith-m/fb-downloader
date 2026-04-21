import yt_dlp
import os
import random
import string
import tempfile
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

        # Use /tmp — the only writable directory on Vercel
        tmp_dir = tempfile.gettempdir()  # resolves to /tmp
        
        is_audio_only = video_format in ['mp3', 'aac', 'wav', 'm4a']
        ext = audio_format if (audio_format != 'best' and is_audio_only) else video_format
        filename = f"{platform}_{unique_id}.{ext}"
        output_path = os.path.join(tmp_dir, filename)

        # Format selection
        if is_audio_only:
            format_selection = f'bestaudio/{audio_format}' if audio_format != 'best' else 'bestaudio/best'
        elif video_quality != 'best':
            format_selection = f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]'
        else:
            format_selection = 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': format_selection,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': video_format if not is_audio_only else None,
        }

        if platform == 'instagram':
            cookie_file = './instagram_cookies.txt'
            if os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # yt-dlp sometimes appends the real extension — find the actual file
        actual_path = output_path
        if not os.path.exists(actual_path):
            # Search /tmp for the file with our unique_id prefix
            for f in os.listdir(tmp_dir):
                if unique_id in f:
                    actual_path = os.path.join(tmp_dir, f)
                    filename = f
                    break

        if not os.path.exists(actual_path):
            return jsonify({'success': False, 'error': 'File not found after download'}), 500

        # Clean up the temp file after sending
        @after_this_request
        def remove_file(response):
            try:
                os.remove(actual_path)
            except Exception:
                pass
            return response

        return send_file(
            actual_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)