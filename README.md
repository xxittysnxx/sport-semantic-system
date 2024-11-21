# Sports Semantic Action Search System

This is a The University of Texas at Dallas Multimedia System Course Projects.

## Project Structure

The code for this project is split into 3 directories:

- `frontend`: contains the upload and search interface.
- `backend`: contains the logic for handle the uploaded video to the server and the processed data into database.
- `MySQL`: contains data stores the video annotations.
- `yolo machine learning`: wait for update.


## Setup

First open MySQL and do the query:

```
-- 1. Create Schema
CREATE SCHEMA SportSemanticSystem;

-- 2. Create 'videos' table
CREATE TABLE SportSemanticSystem.videos (
    video_id INT AUTO_INCREMENT PRIMARY KEY,
    video_url VARCHAR(255) NOT NULL
);

-- 3. Create 'annotations' table
CREATE TABLE SportSemanticSystem.annotations (
    annotation_id INT AUTO_INCREMENT PRIMARY KEY,
    video_id INT NOT NULL,
    tag VARCHAR(50) NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES SportSemanticSystem.videos(video_id) ON DELETE CASCADE
);

-- 4. Create User and Grant Permissions
CREATE USER 'new_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON SportSemanticSystem.* TO 'new_user'@'localhost';
FLUSH PRIVILEGES;
```

To setup the server, make sure to install all needed package:

```
pip install flask flask_cors pymysql
```

Then for the web interface, run the following command in `frontend`:

```
npm install
```

## Running

To run the project, first start the server, then start web interface on the same device.

### Server and Web Interface

To run the server and web interface, execute the following command first in the `backend` directory:

```
python app.py
```

Then in the `frontend` directory. Note, these should be executed in seperate terminals:

```
npm start
```

Once the react web interface is started, a tab should automatically open in your browser displaying the interface. If not, you can visit [http://localhost:3000](http://localhost:3000) to view it in your browser.

*For some public networks that block internal communication, such as CometNet, you'll need to connect both your mobile device and server/web interface to the same private VPN. 
