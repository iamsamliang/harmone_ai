// content-script.js
console.log("content.js active");

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    console.log("Message received in content script");
    if (request.action === "getYoutubeVideoCurrentTime") {
      const videoTime = getYoutubeVideoCurrentTime();
      sendResponse({ time: videoTime });
    }
    return true; // Keep the messaging channel open for sendResponse
  }
);

function getYoutubeVideoCurrentTime() {
  const videoPlayer = document.querySelector('video.html5-main-video');
  if (videoPlayer) {
    return videoPlayer.currentTime;
  } else {
    console.error("No video player found");
    return null;
  }
}
