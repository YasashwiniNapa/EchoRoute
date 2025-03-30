from flask import Flask, render_template, request
import requests
# import serial 
# import time

# # PORT = 'COM5'
# # arduino = serial.Serial(port=PORT, baudrate=115200)
# try:
#     arduino.close()
# except Exception as e:
#     print(e)

# arduino = serial.Serial(port=PORT, baudrate=115200)

app = Flask(__name__)

def get_place_id(query):
    query = query.replace(" ", "+")
    headers = {
        'User-Agent': 'SmartNavApp/1.0 (avani.jagdale@gmail.com)'
    }
    searchurl = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    
    response = requests.get(searchurl, headers=headers)
    response = response.json()
    place = response[0]
    return (place['lat'], place['lon'])

def get_directions(start, stop):
    profile = 'driving'
    (lat1, lon1) = start
    (lat2, lon2) = stop
    BASE_URL = f"http://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}?overview=full&steps=true"
  
    response = requests.get(BASE_URL)
    data = response.json()

    steps = data['routes'][0]['legs'][0]['steps']
    dir=[]
    for i, step in enumerate(steps):
        instruction = step['maneuver']['modifier']  # Text instruction
        distance_km = step['distance'] / 1000  # Convert meters to km
        street_name = ""  # Default value

        # If 'name' is in the step (street name information)
        if 'name' in step:
            street_name = f"on {step['name']}"

        # Print the instruction with street name and distance
        # arduino.write((f"{instruction} {street_name}\t{distance_km:.1f}km").encode())
        # time.sleep(1)
        # if arduino.in_waiting > 0:
        #     response = arduino.readline().decode().strip()
        #     print(f"Received: {response}")
        # else:
        #     print("No response received.")
        
        dir.append(f"{instruction} {street_name}\t{distance_km:.1f}km")

    return dir    


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_address = request.form['start_address']
        stop_address = request.form['stop_address']
        
        # Get coordinates for both addresses
        start_coords = get_place_id(start_address)
        stop_coords = get_place_id(stop_address)
        
        if start_coords == (None, None) or stop_coords == (None, None):
            return render_template('index.html', error="Invalid address")

        # Get directions
        steps = get_directions(start_coords, stop_coords)
        print(steps)
        return render_template('index.html', steps=steps, start=start_address, stop=stop_address)

    return render_template('index.html', steps=None)

if __name__ == '__main__':
    app.run(debug=True)
