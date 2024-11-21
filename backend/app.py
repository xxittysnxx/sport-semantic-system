from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
from werkzeug.utils import secure_filename

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

    # Simulate video annotation
    annotations = [
        {"tag": "running", "start_time": 0.0, "end_time": 5.0},
        {"tag": "jumping", "start_time": 5.0, "end_time": 10.0}
    ]
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
