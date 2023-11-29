function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    console.log("Stopping recording");
    mediaRecorder.stop();  // This triggers the "stop" event for mediaRecorder
  }
}

// Additional logic to interact with YouTube page if needed
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startRecording') {
    setupWebSocket();
  }
  if (message.action === 'closeWebSocket') {
    stopRecording();
    if (ws) {
      ws.close();
      console.log('WebSocket connection closed');
    }
  }
});


// Establish a WebSocket connection to the server
let ws = null;
let stream = null;
let mediaRecorder = null;
let clientId = null;
let ytUrl = window.location.href;

function setupWebSocket() {
  chrome.runtime.sendMessage({ action: "getClientId" }, function(response) {
      clientId = response.clientId;
      console.log("Client id: ", clientId);
      console.log("Setting up websocket");
      // ws = new WebSocket(`wss://your-backend-domain/ws/${clientId}`);
      ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`); // localhost testing
      ws.onopen = function(event) {
        console.log('WebSocket connection established');
        startRecording();
      };

      ws.onmessage = async function(event) {
        // Handle incoming message from the server
        await handleServerMessage(event.data);
      };

      ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        ws.close()
      };

      ws.onclose = function(event) {
        console.log('WebSocket connection closed:', event);
        stopRecording();
        ws = null;
      };
  });
}

let currentVideoTimestamp = null;
let timestampCheckInterval = null;

function updateCurrentVideoTimestamp() {
  const video = document.querySelector('video');
  if (video) {
    currentVideoTimestamp = video.currentTime;
  }
}

function startTimestampCheck() {
  timestampCheckInterval = setInterval(updateCurrentVideoTimestamp, 500); // Check every 100ms
}

function stopTimestampCheck() {
  if (timestampCheckInterval) {
    clearInterval(timestampCheckInterval);
    timestampCheckInterval = null;
  }
}

async function handleServerMessage(message) {
  try {
    if (message.type === 'error') {
      console.error('Error from server:', message.message);
      // Handle the error appropriately in the client
      // This could involve showing an error notification to the user, etc.
    } else if (typeof message === "string") {
        // Handle text message
        let parsedMessage = JSON.parse(message);
        if (parsedMessage.type === "text") {
            console.log("Text data: ", parsedMessage.data);
            // Process text data...
        }
    } else if (message instanceof Blob) {
        // Handle binary message (audio data)
        // Process audio data...
        console.log('Received audio from server');
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const arrayBuffer = await message.arrayBuffer();

        try {
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            // Play the decoded audio
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination); // Connect to speakers
            source.start(); // Play the audio
        } catch (e) {
            console.error('Error decoding audio:', e);
        }
    }
  } catch (error) {
    console.error('Error processing message from server:', error);
  }
}

function getCurrentTabUrl() {
  return window.location.href;
}


// For testing purposes only
function downloadAudioBlob(audioBlob) {
  const url = URL.createObjectURL(audioBlob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = 'recorded_audio.webm';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a); // Clean up by removing the element
  window.URL.revokeObjectURL(url); // Free up memory by revoking the blob URL
  console.log("Downloading audio file")
}

async function startRecording() {
  try {
    // const timestamp = getCurrentVideoTimestamp();
    // if (timestamp === null) {
    //     console.error('No video found or video not playing')
    // }
    console.log("Starting recording");
    startTimestampCheck();
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    console.log("Microphone enabled");
    
    mediaRecorder.addEventListener("dataavailable", event => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        console.log("Sending data over socket");
        ws.send(JSON.stringify({
          type: 'timestamp',
          timestamp: currentVideoTimestamp,
          ytUrl: ytUrl
        }));

        // Then, send the audio chunk as binary data
        ws.send(event.data);
        console.log("Data successfully sent over socket");
      }
    });
    
    mediaRecorder.addEventListener("stop", () => {
      stopTimestampCheck();
      stream.getTracks().forEach(track => track.stop());
      // Optionally, send a message indicating recording end
      // if (ws && ws.readyState === WebSocket.OPEN) {
      //   ws.send(JSON.stringify({ type: 'endOfStream' }));
      // }
    });
    
    mediaRecorder.start(1000); // 1000 tells it to send data every second over socket
      
  } catch (error) {
      console.error('Error accessing media devices:', error);
  }
}

// Function to get the current timestamp of the YouTube video
// function getCurrentVideoTimestamp() {
//   const video = document.querySelector('video');
//   if (video) {
//     return video.currentTime; // currentTime gives the current playback position in seconds
//   }
//   return null;
// }
  
  // async function startRecording() {
    //   try {
      //     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      //     const mediaRecorder = new MediaRecorder(stream);
//     const audioChunks = [];

//     mediaRecorder.addEventListener("dataavailable", event => {
//       audioChunks.push(event.data);
//     });

//     // let silenceTimer;
//     // mediaRecorder.addEventListener("start", () => {
//     //   stream.getAudioTracks()[0].onended = () => {
//     //     clearTimeout(silenceTimer);
//     //     mediaRecorder.stop();
//     //   };
//     // });

//     mediaRecorder.addEventListener("stop", () => {
//       const audioBlob = new Blob(audioChunks);
//       downloadAudioBlob(audioBlob);
//       // Cleanup tasks
//       stream.getTracks().forEach(track => track.stop()); // Stop the media stream
//     });

//     // mediaRecorder.addEventListener("stop", () => {
//     //   const audioBlob = new Blob(audioChunks);
//     //   sendDataToBackend(audioBlob);
//     //   stream.getTracks().forEach(track => track.stop()); // Stop the media stream
//     // });

//     console.log("Recording of user voice starting")
//     mediaRecorder.start();

//     // stop recording after 5 seconds
//     setTimeout(() => {
//       if (mediaRecorder.state === "recording") {
//         mediaRecorder.stop();
//         console.log("Recording of user voice ending")
//       }
//     }, 5000);

//     // // Detect silence
//     // // Implement logic to reset `silenceTimer` when speech is detected
//     // silenceTimer = setTimeout(() => {
//     //   mediaRecorder.stop(); // Stop recording after 2 seconds of silence
//     // }, 2000);
//   } catch (error) {
//     console.error('Error accessing media devices:', error);
//   }
// }