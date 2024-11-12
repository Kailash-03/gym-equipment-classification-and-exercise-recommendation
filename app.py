from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import requests
from werkzeug.utils import secure_filename
import os



# Load the trained model
model = load_model('gym_equipment_classifier.h5')
class_names = ['Barbell', 'Bench Press', 'Kettlebell', 'Pull-up_bar','Resistance bands','aerobic_steppers', 'Dumb_bell']

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


from dotenv import load_dotenv
import google.generativeai as genai
import markdown2

def get_exercises(equipment_type):
    """Gets exercise recommendations for a given equipment type.

    Args:
        equipment_type (str): The type of equipment, e.g., "dumbbell", "barbell", "yoga mat".

    Returns:
        str: A string containing exercise recommendations.
    """

    load_dotenv()
    genai.configure(api_key=os.getenv("API_KEY"))

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Provide a list of exercises that can be performed using {equipment_type}. Please include detailed instructions and safety tips."
    response = model.generate_content(prompt)
    
    html_content = markdown2.markdown(response.text)
    return html_content


@app.route('/')
def home():
    return render_template('index.html')

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
        
        # Get predictions
        predicted_class, confidence = predict_equipment(filepath)
        
        # Get exercise recommendations
        exercises = get_exercises(predicted_class)
        
        return render_template('index.html',
                             prediction=predicted_class,
                             confidence=round(confidence * 100, 2),
                             exercises=exercises)

if __name__ == '__main__':
    app.run(debug=True)