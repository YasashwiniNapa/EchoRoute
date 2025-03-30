from flask import Flask, request, jsonify
import whisper
import os
import re
from osmap import get_place_id, get_directions  # Import functions from osmap.py

app = Flask(__name__)

#load whisper model
model = whisper.load_model("base")

def extract_addresses(text):
    """
    Extract start and end locations from transcribed text.
    Expected format: "from [start] to [end]"
    """
    match = re.search(r'from (.+?) to (.+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join(os.getcwd(), 'audio.wav')

    audio_file.save(audio_path)
    print(f"Audio file saved at: {audio_path}")

    try:
        #transcribe audio
        print(f"Attempting to transcribe: {audio_path}")
        result = model.transcribe(audio_path)
        transcribed_text = result['text']
        print(f"Transcription result: {transcribed_text}")

        #extract addresses
        start_address, end_address = extract_addresses(transcribed_text)
        if not start_address or not end_address:
            return jsonify({'error': 'Could not extract addresses from speech'}), 400

        #get coords of starting and ending locs
        start_coords = get_place_id(start_address)
        end_coords = get_place_id(end_address)
        if not start_coords or not end_coords:
            return jsonify({'error': 'Invalid address detected'}), 400

        steps = get_directions(start_coords, end_coords)

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        os.remove(audio_path)
        print("Cleaned up the file.")

    return jsonify({
        'transcription': transcribed_text,
        'start_address': start_address,
        'end_address': end_address,
        'start_coordinates': start_coords,
        'end_coordinates': end_coords,
        'directions': steps
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
