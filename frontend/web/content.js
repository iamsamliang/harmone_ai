// content-script.js
console.log("content.js active");

// Function to save the current time of the YouTube video to chrome.storage.session
function saveCurrentTime() {
  const videoPlayer = document.querySelector('video.html5-main-video');
  if (videoPlayer) {
    // Save the current time of the video in chrome.storage.session
    chrome.storage.session.set({ 'youtubeVideoCurrentTime': videoPlayer.currentTime }, function() {
      if (chrome.runtime.lastError) {
        console.error("Error setting currentTime in storage:", chrome.runtime.lastError);
      } else {
        console.log("Current time saved:", videoPlayer.currentTime);
      }
    });
  } else {
    console.error("No video player found");
  }
}

// Run saveCurrentTime function periodically
setInterval(saveCurrentTime, 1000); // Saves the time every 5 seconds