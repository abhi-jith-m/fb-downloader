import yt_dlp
import os
import random
import string
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Function to generate a random string of fixed length
def generate_unique_id(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Generate a unique random ID
        unique_id = generate_unique_id()  # Generate a random string for uniqueness
        video_filename = f"videoplayback_{unique_id}.mp4"  # Use unique ID in filename
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join('static', 'videos', video_filename),  # Save with unique filename
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)

        # Return the path to the downloaded video (can be used in frontend)
        return jsonify({'success': True, 'filename': video_filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static/videos', exist_ok=True)  # Ensure the 'static/videos' directory exists
    app.run(debug=True)
