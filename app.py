from flask import Flask, request, jsonify, render_template_string
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename

# Load the trained model
model = load_model('gym_equipment_classifier.h5')
class_names = ['Barbell', 'Bench Press', 'Kettlebell', 'Pull-up bar', 'Resistance Bands', 'Aerobic Steppers', 'Dumbbell']

# Load exercise dataset
exercise_df = pd.read_csv('exercise_dataset.csv', encoding='ISO-8859-1')  # Assumes columns ['Equipment', 'Muscle', 'Exercise', 'Instructions']

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_equipment(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])
    return predicted_class, confidence

def get_muscle_groups(equipment_type):
    return exercise_df[exercise_df['Equipment'].str.lower() == equipment_type.lower()]['Muscle'].unique().tolist()

def get_exercises(equipment_type, muscle_group):
    filtered_exercises = exercise_df[(exercise_df['Equipment'].str.lower() == equipment_type.lower()) &
                                     (exercise_df['Muscle'].str.lower() == muscle_group.lower())]
    return filtered_exercises[['Exercise', 'Instructions']].to_dict(orient='records')
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
            body {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            .container {
                margin-top: 50px;
            }
            .card {
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                background-color: #ffffff;
            }
            .btn-primary {
                background-color: #007bff;
                border-color: #007bff;
            }
            .btn-primary:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            .output {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }
            h2, h3 {
                color: #007bff;
            }
            p, li {
                font-size: 16px;
            }
            .upload-section {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }
            .upload-section input {
                max-width: 350px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1 class="text-center">Gym Equipment Identifier</h1>
                <div class="upload-section">
                    <form action="/predict" method="post" enctype="multipart/form-data">
                        <input type="file" name="image" class="form-control mb-3" required>
                        <button type="submit" class="btn btn-primary">Identify Equipment</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)
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
        
        # Predict equipment
        predicted_class, confidence = predict_equipment(filepath)
        
        # Get muscle groups for the predicted equipment
        muscle_groups = get_muscle_groups(predicted_class)
        
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prediction Result</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{
                    background-color: #f8f9fa;
                    font-family: Arial, sans-serif;
                }}
                .container {{
                    margin-top: 50px;
                }}
                .card {{
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    background-color: #ffffff;
                }}
                .btn-primary {{
                    background-color: #007bff;
                    border-color: #007bff;
                }}
                .btn-primary:hover {{
                    background-color: #0056b3;
                    border-color: #0056b3;
                }}
                .output {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                }}
                h2, h3 {{
                    color: #007bff;
                }}
                p, li {{
                    font-size: 16px;
                }}
                .upload-section {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }}
                .upload-section input {{
                    max-width: 350px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h2 class="text-center">Predicted Equipment: {predicted_class} (Confidence: {round(confidence * 100, 2)}%)</h2>
                    <form action="/get_exercises" method="post" class="text-center">
                        <input type="hidden" name="equipment" value="{predicted_class}">
                        <div class="mb-3">
                            <label for="muscle_group" class="form-label">Select Muscle Group:</label>
                            <select name="muscle_group" id="muscle_group" class="form-select" style="max-width: 350px; margin: auto;">
                                {''.join(f'<option value="{muscle}">{muscle}</option>' for muscle in muscle_groups)}
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Get Exercises</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        '''
        return render_template_string(html)
@app.route('/get_exercises', methods=['POST'])
def get_exercises_route():
    equipment_type = request.form['equipment']
    muscle_group = request.form['muscle_group']
    
    exercises = get_exercises(equipment_type, muscle_group)
    
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exercise Recommendations</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            .container {
                margin-top: 50px;
            }
            .card {
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                background-color: #ffffff;
            }
            .btn-primary {
                background-color: #007bff;
                border-color: #007bff;
            }
            .btn-primary:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            .output {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }
            h2, h3 {
                color: #007bff;
            }
            p, li {
                font-size: 16px;
            }
            .list-group-item {
                font-size: 16px;
            }
            .upload-section {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card output">
                <h3 class="text-center">Exercise Recommendations</h3>
                <ul class="list-group">
    '''
    
    if exercises:
        for exercise in exercises:
            html += f"<li class='list-group-item'><h3>{exercise['Exercise']}</h3><br>{exercise['Instructions']}</li>"
    else:
        html += '<p>No exercises found for the selected muscle group.</p>'
    
    html += '''
                </ul>
                <a href="/" class="btn btn-primary mt-3 d-block mx-auto">Upload another image</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)