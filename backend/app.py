from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Set the upload folder as a static directory for video files
app.config['VIDEO_FOLDER'] = os.path.join(os.getcwd(), UPLOAD_FOLDER)

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'user'
DB_PASSWORD = 'password'
DB_NAME = 'SportSemanticSystem'

def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files['video']
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO videos (video_url) VALUES (%s)', (file_path,))
    video_id = cursor.lastrowid
    conn.commit()

    # Load the YOLO model
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model/source/runs/classify/train/weights/best.pt")
    model = YOLO(model_path)

    # Open the video file
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        print("Error: Cannot open video.")
        exit()

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        print("Warning: FPS is 0. Using set value.")
        fps = 100  # Set fallback value
    frame_duration = 1000 / fps  # Duration of one frame in milliseconds
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"FPS: {fps}, Total frames: {total_frames}")

    results = [] # To store results
    frame_count = 0 # Initialize frame counter

    while cap.isOpened():
        ret, frame = cap.read()
        print(f"Reading frame {frame_count}, ret={ret}")
        if not ret:
            break

        # Resize frame if needed
        resized_frame = cv2.resize(frame, (256, 256))  # Adjust to match your model's input size
        # Perform inference
        pred_results = model(resized_frame)  # YOLO inference
        print(f"Prediction results: {pred_results}")

        # Extract the top prediction
        if pred_results and pred_results[0].probs is not None:
            top_class = pred_results[0].probs.top1  # Get the class with the highest probability
            label = model.names[top_class]
        else:
            label = "Unknown"

        # Record result
        timestamp = round(frame_count * frame_duration)  # Timestamp in milliseconds
        results.append({"time_ms": timestamp, "sport": label})
        print(f"Time: {timestamp}ms, Sport: {label}")

        frame_count += 1

    # Release video capture
    cap.release()

    annotations = []
    current_tag = results[0]["sport"]
    start_time = results[0]["time_ms"]

    # Create annotations
    for i in range(1, len(results)):
        if results[i]["sport"] != current_tag:
            end_time = results[i - 1]["time_ms"]
            if end_time - start_time >= 300:
                annotations.append({"tag": current_tag, "start_time": start_time / 1000, "end_time": end_time / 1000})
            current_tag = results[i]["sport"]
            start_time = results[i]["time_ms"]
    if results[-1]["time_ms"] - start_time >= 300:
        annotations.append({"tag": current_tag, "start_time": start_time / 1000, "end_time": results[-1]["time_ms"] / 1000})

    # Print results
    print(f"FPS: {fps}, Total frames: {total_frames}")
    print(f"Results: {annotations}")
 
    for annotation in annotations:
        cursor.execute('INSERT INTO annotations (video_id, tag, start_time, end_time) VALUES (%s, %s, %s, %s)',
                       (video_id, annotation['tag'], annotation['start_time'], annotation['end_time']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "video_id": video_id})

@app.route('/videos/<filename>')
def serve_video(filename):
    try:
        print(f"Serving video from: {os.path.join(app.config['VIDEO_FOLDER'], filename)}")  # Debugging line
        return send_from_directory(app.config['VIDEO_FOLDER'], filename)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging line
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_tags():
    tag = request.args.get('tag')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.annotation_id, v.video_url, a.tag, a.start_time, a.end_time
        FROM annotations a
        JOIN videos v ON a.video_id = v.video_id
        WHERE a.tag LIKE %s
    ''', (f"%{tag}%",))
    results = [{"annotation_id": row[0], "video_url": row[1], "tag": row[2], "start_time": row[3], "end_time": row[4]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
