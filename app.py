import yt_dlp
import os
import random
import string
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def generate_unique_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    platform = data.get('platform', 'youtube')  # Default to youtube if not specified
    video_format = data.get('videoFormat', 'mp4')
    audio_format = data.get('audioFormat', 'best')
    video_quality = data.get('videoQuality', 'best')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        unique_id = generate_unique_id()
        output_filename = f"videoplayback_{unique_id}"
        output_path = os.path.join('static', 'videos', output_filename)
        
        # Configure format based on user selections
        if video_quality == 'best':
            format_selection = f'bestvideo[ext={video_format}]+bestaudio[ext={audio_format}]/best[ext={video_format}]'
        else:
            # Format selection based on resolution
            format_selection = f'bestvideo[height<={video_quality}][ext={video_format}]+bestaudio[ext={audio_format}]/best[height<={video_quality}][ext={video_format}]'
        
        # Special handling for MP3 (audio only)
        if audio_format == 'mp3' and video_format == 'mp4':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                return jsonify({'success': True, 'filename': f'{output_filename}.mp3'})
        
        # Regular video download
        ydl_opts = {
            'format': format_selection,
            'outtmpl': f'{output_path}.%(ext)s',
            'merge_output_format': video_format,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            
            # Get the actual filename with extension
            base, _ = os.path.splitext(downloaded_file)
            actual_file = f"{base}.{video_format}"
            filename = os.path.basename(actual_file)
            
            return jsonify({'success': True, 'filename': filename})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/videos', exist_ok=True)
    app.run(debug=True)