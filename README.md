# Exercise_suggestion_project
This project is a Flask web application that classifies gym equipment from uploaded images and provides exercise recommendations based on the classified equipment. The model is trained using TensorFlow (MobileNetV2) and Keras.



## Project Structure
```
.env
app.py
Dataset/
    aerobic_steppers/
    Barbell/
    Bench Press/
    dumb_bell/
    Kettlebell/
    Pull-up_bar/
    Resistance bands/
Gym_Equipment_Classification.ipynb
gym_equipment_classifier.h5
templates/
    index.html
uploads/
```

## How to run the project

1. Clone the repository
2. Add gemini API key and secret to the .env file
3. Install the required libraries using the following command:
```bash
pip install -r requirements.txt
```
4. Run the following command to start the server:
```bash
python app.py
```