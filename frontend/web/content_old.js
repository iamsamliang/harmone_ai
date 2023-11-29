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

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.type === "startRecording") {
      console.log("Received recording request");
      startRecording(5000); // Start recording for 5 seconds
  }
});

async function startRecording(duration) {
  try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
      console.log("Recording started");

      // Create an instance of MediaRecorder
      const recorder = new MediaRecorder(stream);

      // Array to hold the recorded data chunks
      let dataChunks = [];

      recorder.ondataavailable = (event) => {
          // Push each chunk (blob) of data to the array
          dataChunks.push(event.data);
      };

      recorder.onstop = async () => {
          // Combine all the chunks into a single Blob
          const audioBlob = new Blob(dataChunks, { type: recorder.mimeType });

          // Create a URL for the blob
          let audioUrl = URL.createObjectURL(audioBlob);

          // Use a temporary anchor element to trigger the download
          const downloadLink = document.createElement('a');
          downloadLink.href = audioUrl;
          downloadLink.setAttribute('download', 'recording.webm'); // You can use a different file name and format
          document.body.appendChild(downloadLink);
          downloadLink.click();
          document.body.removeChild(downloadLink);
          
          // Clean up by revoking the blob URL and resetting dataChunks
          URL.revokeObjectURL(audioUrl);
          dataChunks = [];
          console.log("Recording stopped and download should start now");
      };

      // Start recording
      recorder.start();

      // Stop recording after 'duration' milliseconds
      setTimeout(() => {
          recorder.stop();

          // Stop all media tracks as well
          stream.getTracks().forEach(track => track.stop());
      }, duration);
  } catch (error) {
      console.error("Error starting recording:", error.message);
  }
}


