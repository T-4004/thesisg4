// script.js

// JavaScript function to refresh the page
function refreshPage() {
    location.reload();
}

// Check if the video feed has loaded successfully
document.getElementById('video-feed').onload = () => {
    console.log('Video feed loaded');
    // Show the refresh button
    document.getElementById('refresh-button-container').style.display = 'block';
};

// Handle error if face detection fails
document.getElementById('video-feed').onerror = () => {
    console.error('Error loading video feed');
    // Show the error message
    document.getElementById('error-message').style.display = 'block';
};
