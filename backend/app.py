import os
from flask import Flask, request, jsonify
from fiber_identification import identify_fiber_in_image
from stroke_identification import identify_stroke_in_image
from particle_color_size import predict_tea_variant_from_image
from predictions.infusion_predict import color_features_infusion_predict
from predictions.liquid_predict import color_features_liquid_predict
from flask_cors import CORS
from werkzeug.utils import secure_filename

from PIL import Image
import io
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to convert an image array to Base64
def image_to_base64(image_array):
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Endpoint: Identify Fiber
@app.route('/identify-fiber', methods=['POST'])
def identify_fiber():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read image and convert to OpenCV format
    image = Image.open(file).convert('RGB')
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Identify fiber
    result_image, stats = identify_fiber_in_image(image)

    print("Stats returned to frontend:", stats)

    # Convert result to base64
    result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
    result_base64 = image_to_base64(result_image_rgb)

    return jsonify({
        "statistics": stats,
        "result_image": result_base64
    })

# Endpoint: Identify Stroke
@app.route('/identify-stroke', methods=['POST'])
def identify_stroke():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read image and convert to OpenCV format
    image = Image.open(file).convert('RGB')
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Identify stroke
    result_image, stats = identify_stroke_in_image(image)

    print("Stats returned to frontend:", stats)

    # Convert result to base64
    result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
    result_base64 = image_to_base64(result_image_rgb)

    return jsonify({
        "statistics": stats,
        "result_image": result_base64
    })

# Endpoint: Predict Tea Elevation
@app.route('/predict_liquid', methods=['POST'])
def predict_liquid():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        prediction = color_features_liquid_predict(filepath)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Predict Tea Elevation
@app.route('/predict_infusion', methods=['POST'])
def predict_infusion():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        prediction = color_features_infusion_predict(filepath)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Predict Tea Variant 
@app.route('/predict_tea_variant', methods=['POST'])
def predict_variant():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        prediction = predict_tea_variant_from_image(filepath)
        print("Prediction returned to frontend:", prediction)
        return jsonify({'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Generate Full Tea Report
@app.route('/generate_report', methods=['POST'])
def generate_report():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # --- 1. Tea Variant Prediction ---
        tea_variant = predict_tea_variant_from_image(filepath)

        # --- 2. Fiber Statistics & Image ---
        image = Image.open(filepath).convert('RGB')
        image_np = np.array(image)
        image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        fiber_image_cv2, fiber_stats = identify_fiber_in_image(image_cv2)
        fiber_image_base64 = image_to_base64(cv2.cvtColor(fiber_image_cv2, cv2.COLOR_BGR2RGB))

        # --- 3. Stroke Statistics & Image ---
        stroke_image_cv2, stroke_stats = identify_stroke_in_image(image_cv2)
        stroke_image_base64 = image_to_base64(cv2.cvtColor(stroke_image_cv2, cv2.COLOR_BGR2RGB))

        # Add additional calculated ratio fields if needed
        fiber_stats["fiber_percentage"] = round(fiber_stats["fiber_percentage"], 2)
        stroke_stats["brown_particle_ratio"] = round(stroke_stats["brown_particle_ratio"], 2)

        return jsonify({
            'tea_variant': tea_variant,
            'fiber_statistics': fiber_stats,
            'fiber_image': fiber_image_base64,
            'stroke_statistics': stroke_stats,
            'stroke_image': stroke_image_base64
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8080)
