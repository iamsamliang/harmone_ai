// content.js
console.log("content.js active");

function saveCurrentTime() {
  const videoPlayer = document.querySelector('video.html5-main-video');
  if (videoPlayer) {
    console.log("Current time: " + videoPlayer.currentTime);
    chrome.runtime.sendMessage({ type: "current_time", currentTime: videoPlayer.currentTime });
  } else {
    console.error("No video player found");
  }
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.type == "notifications") {
    saveCurrentTime();
  }
});

