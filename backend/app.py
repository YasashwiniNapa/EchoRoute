from flask import Flask, request, jsonify, render_template
import whisper
import os
import re
import requests

# final py file -- combines whisper llm model & osm api for final output

app = Flask(__name__)

#load whisper model
model = whisper.load_model("base")

def extract_addresses(text):
    """
    Extracts start and end locations from transcribed text.
    Expected format: "from [start] to [end]"
    """
    match = re.search(r'from (.+?) to (.+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def get_place_id(query):
    """
    Converts a location name into latitude and longitude using OpenStreetMap API.
    """
    query = query.replace(" ", "+")
    headers = {'User-Agent': 'SmartNavApp/1.0 (avani.jagdale@gmail.com)'}
    search_url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"

    response = requests.get(search_url, headers=headers)
    response = response.json()

    if response:
        place = response[0]
        return (place['lat'], place['lon'])
    
    return None

def get_directions(start, stop):
    """
    Fetches driving directions using OSRM.
    """
    profile = 'driving'
    (lat1, lon1) = start
    (lat2, lon2) = stop
    BASE_URL = f"http://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}?overview=full&steps=true"

    response = requests.get(BASE_URL)
    data = response.json()

    if 'routes' not in data or not data['routes']:
        return []

    steps = data['routes'][0]['legs'][0]['steps']
    directions = []

    for step in steps:
        #print(f"Processing Step: {step}")  # Print the full step object
        if step['maneuver']['type'] != 'arrive' and step['maneuver']['type'] != 'depart':
            instruction = step['maneuver']['modifier']
            distance_km = step['distance'] / 1000  # Convert meters to km
            street_name = step.get('name', '')  # Get street name if available
            if len(street_name) < 1:
                street_name = step.get('destinations', '')
            direction = f"{instruction} on {street_name} ({distance_km:.1f} km)"
            directions.append(direction)
            #print(f"Direction: {direction}")  # Print the formatted direction
            
    #print(f"Final Directions List: {directions}") 
    for i, d in enumerate(directions):
        print(f"{i+1}. {d}")
    #print directions list 
    return directions  

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join(os.getcwd(), 'audio.wav')

    audio_file.save(audio_path)
    print(f"Audio file saved at: {audio_path}")

    try:
        #transcribed audio
        print(f"Attempting to transcribe: {audio_path}")
        result = model.transcribe(audio_path)
        transcribed_text = result['text']
        print(f"Transcription result: {transcribed_text}")

        #extract addresses
        start_address, end_address = extract_addresses(transcribed_text)
        print(f"Start Address: {start_address}, End Address: {end_address}")
        if not start_address or not end_address:
            return jsonify({'error': 'Could not extract addresses from speech'}), 400

        #get coordinates of start & end locs
        start_coords = get_place_id(start_address)
        end_coords = get_place_id(end_address)
        print(f"Start Coordinates: {start_coords}, End Coordinates: {end_coords}")
        if not start_coords or not end_coords:
            return jsonify({'error': 'Invalid address detected'}), 400

        steps = get_directions(start_coords, end_coords)

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    finally:
        os.remove(audio_path)
        print("Cleaned up the file.")

    #return formatted response
    return jsonify({
        'transcription': transcribed_text,
        'start_address': start_address,
        'end_address': end_address,
        'start_coordinates': start_coords,
        'end_coordinates': end_coords,
        'directions': steps
    })

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', steps=None)

if __name__ == '__main__':
    app.run(debug=True)
