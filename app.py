from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

app = Flask(__name__)
CORS(app)

# Load the Excel data once
EXCEL_PATH = os.environ.get("EXCEL_PATH", "train.xlsx")
excel_data = pd.read_excel(EXCEL_PATH)

labels_list = [
    'Cherry leaf',
    'Peach leaf',
    'Corn leaf blight',
    'Apple rust leaf',
    'Potato leaf late blight',
    'Strawberry leaf',
    'Corn rust leaf',
    'Tomato leaf late blight',
    'Tomato mold leaf',
    'Potato leaf early blight',
    'Apple leaf',
    'Tomato leaf yellow virus',
    'Blueberry leaf',
    'Tomato leaf mosaic virus',
    'Raspberry leaf',
    'Tomato leaf bacterial spot',
    'Squash Powdery mildew leaf',
    'grape leaf',
    'Corn Gray leaf spot',
    'Tomato Early blight leaf',
    'Apple Scab Leaf',
    'Tomato Septoria leaf spot',
    'Tomato leaf',
    'Soyabean leaf',
    'Bell_pepper leaf spot',
    'Bell_pepper leaf',
    'grape leaf black rot',
    'Potato leaf',
    'Tomato two spotted spider mites leaf'
]
label_colors = {
    'Cherry leaf': (57, 12, 140),
    'Peach leaf': (125, 114, 71),
    'Corn leaf blight': (52, 44, 216),
    'Apple rust leaf': (16, 15, 47),
    'Potato leaf late blight': (111, 119, 13),
    'Strawberry leaf': (101, 214, 112),
    'Corn rust leaf': (229, 142, 3),
    'Tomato leaf late blight': (81, 216, 174),
    'Tomato mold leaf': (142, 79, 110),
    'Potato leaf early blight': (172, 52, 47),
    'Apple leaf': (194, 49, 183),
    'Tomato leaf yellow virus': (176, 135, 22),
    'Blueberry leaf': (235, 63, 193),
    'Tomato leaf mosaic virus': (40, 150, 185),
    'Raspberry leaf': (98, 35, 23),
    'Tomato leaf bacterial spot': (116, 148, 40),
    'Squash Powdery mildew leaf': (119, 51, 194),
    'grape leaf': (142, 232, 186),
    'Corn Gray leaf spot': (83, 189, 181),
    'Tomato Early blight leaf': (107, 136, 36),
    'Apple Scab Leaf': (87, 125, 83),
    'Tomato Septoria leaf spot': (236, 194, 138),
    'Tomato leaf': (112, 166, 28),
    'Soyabean leaf': (117, 16, 161),
    'Bell_pepper leaf spot': (205, 137, 33),
    'Bell_pepper leaf': (108, 161, 108),
    'grape leaf black rot': (255, 202, 234),
    'Potato leaf': (73, 135, 71),
    'Tomato two spotted spider mites leaf': (126, 134, 219)
}

def read_detections(image_id, img_height):
    detections = []
    matched_rows = excel_data[excel_data.iloc[:, 0].astype(str).str.equals(image_id, na=False)]
    for _, row in matched_rows.iterrows():
        label = str(row[1]).strip()
        xmin = int(row[2])
        ymin = int(row[3])
        xmax = int(row[4])
        ymax = int(row[5])
        detections.append({
            "label": label,
            "x": xmin,
            "y": ymin,
            "width": xmax - xmin,
            "height": ymax - ymin
        })

   
    return detections

def draw_boxes(image, detections):
    draw = ImageDraw.Draw(image)
    for det in detections:
        x, y, w, h = det["x"], det["y"], det["width"], det["height"]
        label = det["label"]
        color = label_colors.get(label, (128, 128, 128))
        draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
        draw.text((x + 5, y - 10), label, fill=color)
    return image

@app.route("/", methods=["GET"])
def home():
    return "🩺 X-ray Annotation API is running"

@app.route("/api/image/annotate", methods=["POST"])
def annotate_image():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded."}), 400

    image = Image.open(file.stream).convert("RGB")
    image_id = os.path.splitext(file.filename)[0]
    detections = read_detections(image_id, image.height)
    draw_boxes(image, detections)

    # Create report
    report = list(set(det["label"] for det in detections))

    # Encode image as base64
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({
        "image": img_str,
        "report": report
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
