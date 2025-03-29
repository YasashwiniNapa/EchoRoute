from flask import Flask, request, jsonify
import whisper
import os

app = Flask(__name__)

# base model whisper loaded
model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    #saved as audio.wav every time -- trial
    audio_path = os.path.join(os.getcwd(), 'audio.wav')

 
    audio_file.save(audio_path)
    print(f"Audio file saved at: {audio_path}")

    try:
        print(f"Attempting to transcribe: {audio_path}")
        result = model.transcribe(audio_path)
        print(f"Transcription result: {result['text']}")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
    finally:
        # clean up the saved audio file w/ 200 ok
        os.remove(audio_path)
        print("Cleaned up the file.")

    return jsonify({'transcription': result['text']})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
