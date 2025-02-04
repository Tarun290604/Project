from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import torch
import sys
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Ensure FastSAM is accessible
sys.path.append(os.path.abspath("../FastSAM"))
from FastSAM.fastsam import FastSAM

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Model
def load_model():
    global model
    model_path = "FastSAM-x.pt"  # Ensure the model file is in the correct directory

    try:
        print("Loading FastSAM model...")
        model = FastSAM(model_path)  # Load FastSAM Model
        
        # Handle PyTorch 2.6+ model loading
        try:
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
        except TypeError:
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        print("Model loaded successfully.")

    except Exception as e:
        print(f"Error loading model: {e}")

# Image Preprocessing Function
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return edges

# Joint Space Calculation Function
def calculate_joint_space(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) < 2:
        return [0, 0]  # If not enough contours are detected
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    joint_space_widths = [cv2.boundingRect(cnt)[2] for cnt in contours]
    return joint_space_widths

# Classification Function
def classify_joint_space(joint_space_percentage):
    if joint_space_percentage[0] < 5 or joint_space_percentage[1] < 5:
        return "Grade 3 or 4 (Severe Osteoarthritis)"
    elif joint_space_percentage[0] < 7 or joint_space_percentage[1] < 7:
        return "Grade 2 (Moderate Osteoarthritis)"
    elif joint_space_percentage[0] < 8 or joint_space_percentage[1] < 8:
        return "Grade 1 (Mild Osteoarthritis)"
    elif joint_space_percentage[0] < 10 or joint_space_percentage[1] < 10:
        return "Grade 0 (Normal Joint Space)"
    else:
        return "Invalid (Out of Expected Range)"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        processed_image = preprocess_image(filepath)
        joint_space_widths = calculate_joint_space(processed_image)
        classification = classify_joint_space(joint_space_widths)

        return jsonify({"classification": classification, "joint_space_widths": joint_space_widths})
    
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"})

if __name__ == '__main__':
    load_model()  # Load model on startup
    app.run(debug=True)
