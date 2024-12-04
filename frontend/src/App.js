import React, { useState } from 'react';

function App() {
    const [results, setResults] = useState([]);

    const handleUpload = async (event) => {
        const file = event.target.files[0];
        const formData = new FormData();
        formData.append('video', file);
        await fetch('http://127.0.0.1:5000/upload', { method: 'POST', body: formData });
        alert('Video uploaded and annotated!');
    };

    const handleSearch = async (event) => {
        try {
            const query = event.target.value;
            if (query.trim() === '') return;
            const response = await fetch(`http://127.0.0.1:5000/search?tag=${query}`);
            if (!response.ok) {
                throw new Error('Failed to fetch');
            }
            const data = await response.json();
            setResults(data);
            // handle the data
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    };

    return (
        <div>
            <h1>Sport Semantic Search</h1>
            <h2>Upload Video</h2>
            <input type="file" onChange={handleUpload} />

            <h2>Search Tags</h2>
            <input placeholder="Search for a tag..." onChange={handleSearch} />
            <ul>
                {results.map((res) => (
                    <li key={res.annotation_id}>
                        <a
                            href={`#t=${res.start_time}`}
                            onClick={(e) => {
                                e.preventDefault(); // Prevent the default behavior of the anchor tag
                                const videoFilename = res.video_url.split('/').pop(); // Extract the filename from the URL
                                const videoUrl = `http://127.0.0.1:5000/videos/${videoFilename}`; // Construct the full URL to the video
                                const startTime = res.start_time;
                                const endTime = res.end_time;

                                // Open a new window
                                const videoWindow = window.open('', '_blank'); // Open a blank window

                                // Write HTML content with the video
                                videoWindow.document.write(`
                                    <html>
                                        <head>
                                            <title>Video Playback</title>
                                        </head>
                                        <body>
                                            <video id="videoElement" controls>
                                                <source src="${videoUrl}" type="video/mp4">
                                                Your browser does not support the video tag.
                                            </video>
                                            <script>
                                                const videoElement = document.getElementById('videoElement');

                                                // Wait for the video to load
                                                videoElement.onloadeddata = function() {
                                                    // Set the start time when the video is ready
                                                    videoElement.currentTime = ${startTime};
                                                };

                                                // Set the currentTime to the start time when the play button is clicked
                                                videoElement.addEventListener('play', function() {
                                                    videoElement.currentTime = ${startTime};
                                                });

                                                // Stop the video when it reaches the end time
                                                videoElement.ontimeupdate = function() {
                                                    if (videoElement.currentTime >= ${endTime}) {
                                                        videoElement.pause();
                                                        videoElement.currentTime = ${startTime}; // Reset to start time after stopping
                                                    }
                                                };
                                            </script>
                                        </body>
                                    </html>
                                `);
                            }}
                        >
                            {res.tag} ({res.video_url.split('/').pop()}, Start: {res.start_time}s, End: {res.end_time}s)
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
