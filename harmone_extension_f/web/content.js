console.log("content.js active");

// Function to get the current time of the YouTube video player
function getYoutubeVideoCurrentTime() {
  const videoPlayer = document.getElementsByClassName('video-stream')[0];
  if (videoPlayer) {
    return videoPlayer.currentTime;
  } else {
    console.error('No video player found');
    return null;
  }
}

// Function to log the current time of the video player
function logCurrentTime() {
  const currentTime = getYoutubeVideoCurrentTime();
  if (currentTime !== null) {
    console.log('Current video time: ' + currentTime);
  }
}

// Set an interval to log the video time every second
setInterval(logCurrentTime, 1000);
