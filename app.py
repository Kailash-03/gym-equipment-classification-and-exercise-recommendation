from flask import Flask, request, jsonify, render_template_string
from tensorflow.keras.models import load_model
import http.client
import json
import urllib.parse
from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename

# Load the trained model
model = load_model('gym_equipment_classifier.h5')
class_names = ['barbell', 'bench press', 'kettlebell', 'pull-up bar', 'resistance band', 'aerobic stepper', 'dumbbell']

# Load exercise dataset
exercise_df = pd.read_csv('exercise_dataset.csv', encoding='ISO-8859-1')  # Assumes columns ['Equipment', 'Muscle', 'Exercise', 'Instructions']

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API configuration for ExerciseDB
API_KEY = "530d3829afmsh6bb473518d9464fp17031ejsn994684d294d5"
API_HOST = "exercisedb.p.rapidapi.com"
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': API_HOST
}

# Function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to simulate the equipment prediction (replace with actual ML model)
def predict_equipment(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])
    return predicted_class, confidence

#function to fetch the gif url
def get_exercise_gif(exercise_id):
    conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "530d3829afmsh6bb473518d9464fp17031ejsn994684d294d5",
        'x-rapidapi-host': "exercisedb.p.rapidapi.com"
    }
    
    # Make the request to get exercise details by ID
    conn.request("GET", f"/exercises/exercise/{exercise_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status == 200:
        # Parse the JSON response
        exercise_data = json.loads(data.decode("utf-8"))
        # Return the GIF URL or video URL, if available
        return exercise_data.get('gifUrl', '')  # Returns an empty string if no gifUrl is found
    else:
        print(f"Error: {res.status} - {res.reason}")
        return ''  # Return empty string if the request failed or no gif URL is available


def get_muscle_groups(equipment_type):
    # Ensure equipment_type is valid (present in class_names, if it's defined elsewhere)
    if equipment_type not in class_names:
        return []  # If the equipment type is not recognized by the model, return an empty list
    if equipment_type == 'bench press':
        equipment_type = 'smith machine'
    if equipment_type == 'pull-up bar':
        equipment_type = 'upper body ergometer'
    if equipment_type == 'aerobic stepper':
        equipment_type = 'bosu ball'
    
    # Define the connection to the API
    conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    encoded_eq = urllib.parse.quote(equipment_type)
    conn.request("GET", f"/exercises/equipment/{encoded_eq}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    if res.status == 200:
        equipment_data = json.loads(data.decode("utf-8"))
        muscle_groups = list(set([exercise['target'] for exercise in equipment_data if 'target' in exercise]))
        # Return the muscle groups (remove duplicates by using a set)
        return muscle_groups
    else:
        # Handle errors if the API call is unsuccessful
        print(f"Error: {res.status} - {res.reason}")
        return []
    

# Function to get exercises based on equipment and muscle group
def get_exercises(equipment_type, muscle_group):
    if equipment_type not in class_names:
        return []  # Return an empty list if the equipment type is not recognized

    if equipment_type =='bench press':
        equipment_type = 'smith machine'
    if equipment_type == 'pull-up bar':
        equipment_type = 'upper body ergometer'
    if equipment_type == 'aerobic stepper':
        equipment_type = 'bosu ball'
    conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
########
    encoded_eq = urllib.parse.quote(equipment_type)
    conn.request("GET", f"/exercises/equipment/{encoded_eq}", headers=headers)
    res = conn.getresponse()
    data = res.read()

    if res.status == 200:
        exercises_data = json.loads(data.decode("utf-8"))
        
        # Filter exercises by muscle group (based on the target key)
        filtered_exercises = [exercise for exercise in exercises_data if muscle_group.lower() in exercise['target'].lower()]
        return filtered_exercises
    else:
        print(f"Error: {res.status} - {res.reason}")
        return []

# Home route
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gym Equipment Identifier</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* General page styling */
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-image: url("https://images.pexels.com/photos/669578/pexels-photo-669578.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2");
            background-repeat: no-repeat;
            background-size: cover;
            background-position: center;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        /* Background overlay for readability */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 0;
        }

        .container-fluid {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1;
            position: relative;
        }

        .row {
            height: 100%;
        }

        /* Left side image styling */
        .left-side {
            height: 100%;
            width: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        /* Title styling */
        .project-title h1 {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* Right side layout styling */
        .right-side {
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 20px;
        }

        /* Button styling */
        .btn-custom {
            max-width: 350px;
            width: 100%;
            padding: 10px;
            font-size: 1rem;
            color: white;
            background-color: #246fea;
            border: none;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .btn-custom:hover {
            background-color: #307af2;
            color: white;
        }

        /* Video styling */
        video, .upload-section input {
            max-width: 350px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        /* Upload section styling */
        .upload-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        
        /* Ensures elements are above overlay */
        .content {
            position: relative;
            z-index: 1;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row w-100 content">
            <!-- Left side for image -->
            <div class="col-md-6 left-side">
                <div class="project-title">
                    <h1>Gym Equipment Classification and Exercise Recommendation</h1>
                </div>
            </div>

            <!-- Right side for project details and functionality -->
            <div class="col-md-6 right-side">
                <!-- Camera Section -->
                <div class="camera-section">
                    <video id="video" autoplay></video>
                    <canvas id="canvas" style="display: none;"></canvas>
                    <button id="captureBtn" class="btn btn-custom mt-3">Capture & Identify</button>
                </div>

                <!-- Upload Section -->
                <div class="upload-section">
                    <p>Or, upload an image:</p>
                    <form action="/predict" method="post" enctype="multipart/form-data">
                        <input type="file" name="image" class="form-control mb-3">
                        <button type="submit" class="btn btn-custom">Identify from File</button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const captureBtn = document.getElementById('captureBtn');

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
            } catch (error) {
                alert('Camera access denied or unavailable.');
            }
        }

        captureBtn.addEventListener('click', () => {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('image', blob, 'captured_image.jpg');

                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.text();
                document.open();
                document.write(result);
                document.close();
            }, 'image/jpeg');
        });

        window.onload = startCamera;
    </script>
</body>
</html>
    '''
    return render_template_string(html)

# Predict route
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['image']
    if file.filename == '':
        return 'No file selected', 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        predicted_class, confidence = predict_equipment(filepath)
        
        # Fetch muscle groups based on the predicted equipment
        muscle_groups = get_muscle_groups(predicted_class)
        
        # Updated HTML with improved UI for layout and styling
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Prediction Result</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        font-family: Arial, sans-serif;
                        background-image: url("https://images.pexels.com/photos/669578/pexels-photo-669578.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2");
                        background-repeat: no-repeat;
                        background-size: cover;
                        background-position: center;
                        color: white;
                        position: relative;
                    }

                    /* Overlay for background readability */
                    body::before {
                        content: "";
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.6);
                        z-index: 0;
                    }

                    .container {
                        position: relative;
                        z-index: 1;
                        display: flex;
                        width: 80%;
                        padding: 20px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    }

                    .left-section {
                        width: 50%;
                        padding-right: 20px;
                        border-right: 1px solid #ccc;
                    }

                    .right-section {
                        width: 50%;
                        padding-left: 20px;
                    }

                    h2, h3, h4 {
                        color: #f8f9fa;
                        margin-bottom: 15px;
                    }

                    ul {
                        list-style-type: none;
                        padding: 0;
                    }

                    li {
                        padding: 8px 0;
                        font-size: 1.1rem;
                        color: #e0e0e0;
                    }

                    select, button {
                        width: 100%;
                        padding: 10px;
                        font-size: 1rem;
                        border: none;
                        border-radius: 5px;
                        margin-top: 10px;
                    }

                    button {
                        background-color: #f8f9fa;
                        color: #333;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }

                    button:hover {
                        background-color: #ddd;
                    }

                </style>
            </head>
            <body>
                <div class="container">
                    <!-- Left section for displaying equipment info and muscle groups -->
                    <div class="left-section">
                        <h2>Equipment: {{ equipment }}</h2>
                        <h3>Confidence: {{ confidence*100 }}%</h3>
                        <h4>Targeted Muscle Groups:</h4>
                        <ul>
                            {% for muscle in muscle_groups %}
                                <li>• {{ muscle }}</li>
                            {% endfor %}
                        </ul>
                    </div>

                    <!-- Right section for muscle group selection and submission -->
                    <div class="right-section">
                        <h4>Select a Muscle Group for Recommendations:</h4>
                        <form method="POST" action="/exercises">
                            <input type="text" name="equipment" value="{{ equipment }}" hidden>
                            <select name="muscle_group" class="form-select mb-3">
                                {% for muscle in muscle_groups %}
                                    <option value="{{ muscle }}">{{ muscle }}</option>
                                {% endfor %}
                            </select>
                            <button type="submit" class="btn btn-secondary mt-2">Get Exercises</button>
                        </form>
                    </div>
                </div>
            </body>
            </html>
        ''', equipment=predicted_class, confidence=confidence, muscle_groups=muscle_groups)
    else:
        return 'Invalid file type', 400

# Exercise recommendation route
@app.route('/exercises', methods=['POST'])
def exercises():
    equipment_type = request.form.get('equipment')
    muscle_group = request.form.get('muscle_group')

    exercises = get_exercises(equipment_type, muscle_group)

    if not exercises:
        return 'No exercises found', 404

    exercise_cards = []
    for exercise in exercises:
        gif_url = get_exercise_gif(exercise['id'])
        exercise_cards.append({
            'name': exercise['name'],
            'instructions': exercise['instructions'],
            'video_url': gif_url
        })

    return render_template_string(''' 
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exercise Recommendations</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            /* Center container styling */
            body{
                background-image: url("https://images.pexels.com/photos/669578/pexels-photo-669578.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2");
                background-repeat: no-repeat;
                background-size: cover;
                background-position: center;
            }
            /* Page heading */
            h2 {
                text-align: center;
                font-weight: bold;
                margin-top:30px;
                margin-bottom: 30px;
            }

            /* Card styling */
            .card {
                margin-bottom: 20px;
                border: none;
                backgroud-color: #343541;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            }

            .card-body {
                display: flex;
                align-items: flex-start;
                padding: 20px;
            }

            .card-title {
                font-size: 1.5rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 15px;
            }

            /* Left image section */
            .exercise-img {
                width: 40%;
                padding-right: 15px;
            }

            .exercise-img img {
                width: 100%;
                border-radius: 8px;
                object-fit: cover;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }

            /* Right instructions section */
            .exercise-instructions {
                width: 60%;
                height:100%;
            }

            /* Styling for the exercise name */
            .exercise-name {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 20px;
            }

            /* Ordered list styling */
            ol {
                font-size: 1.1rem;
                line-height: 1.6;
                margin-left: 20px;
                color: #333;
            }

            ol li {
                margin-bottom: 10px;
            }

            /* Optional: Style for 'No GIF available' message */
            .no-gif {
                font-size: 1rem;
                color: #888;
                margin-top: 15px;
            }

        </style>
    </head>
    <body>

        <div class="container">
            <h2>Exercise Recommendations</h2>
            {% if exercise_cards %}
                {% for exercise in exercise_cards %}
                <div class="card">
                    <div class="card-body">
                        <!-- Left side for GIF/Image -->
                        <div class="exercise-img">
                            {% if exercise.video_url %}
                                <img src="{{ exercise.video_url }}" alt="{{ exercise.name }}">
                            {% else %}
                                <p class="no-gif">No GIF available for this exercise.</p>
                            {% endif %}
                        </div>

                        <!-- Right side for instructions -->
                        <div class="exercise-instructions">
                            <h2 class="exercise-name">{{ exercise.name }}</h2>
                            <ol>
                                {% for instruction in exercise.instructions %}
                                    <li>{{ instruction }}</li>
                                {% endfor %}
                            </ol>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p>No exercises found.</p>
            {% endif %}
        </div>

    </body>
    </html>
    ''', exercise_cards=exercise_cards)  
if __name__ == '__main__':
    app.run(debug=True)
