import yt_dlp
import os
import random
import string
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to generate a random unique ID
def generate_unique_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Generate a unique filename using the random ID
        unique_id = generate_unique_id()
        filename = f"static/videos/{unique_id}.mp4"

        # yt-dlp options for downloading the video with a unique filename
        ydl_opts = {
            'format': 'best',
            'outtmpl': filename,  # Use the generated unique filename
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)

        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/videos', exist_ok=True)
    app.run(debug=True)
