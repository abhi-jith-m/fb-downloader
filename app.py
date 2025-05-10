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
    video_format = request.json.get('videoFormat', 'mp4')
    audio_format = request.json.get('audioFormat', 'best')
    video_quality = request.json.get('videoQuality', 'best')

    if not video_url or not platform:
        return jsonify({'success': False, 'error': 'Missing URL or platform'}), 400

    try:
        # Generate unique random filename
        unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        video_filename = f"{platform}_{unique_id}.{video_format}"
        output_path = os.path.join('static', 'videos', video_filename)
        
        # Configure format based on quality and format selections
        if video_quality != 'best':
            # Format with quality constraint
            format_selection = f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]'
        else:
            format_selection = f'bestvideo+bestaudio/best'
            
        # Handle audio format preference if audio-only is requested
        if audio_format != 'best' and video_format in ['mp3', 'aac', 'wav', 'm4a']:
            format_selection = f'bestaudio/{audio_format}'
            video_filename = f"{platform}_{unique_id}.{audio_format}"
            output_path = os.path.join('static', 'videos', video_filename)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format_selection,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': video_format,
        }
        
        # Add platform-specific options
        if platform == 'instagram':
            # Check if cookie file exists before using it
            cookie_file = './instagram_cookies.txt'
            if os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Verify the file was actually downloaded
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'File download failed'}), 500
            
        return jsonify({'success': True, 'filename': os.path.basename(output_path)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create directory for downloaded videos if it doesn't exist
    os.makedirs('static/videos', exist_ok=True)
    app.run(debug=True)