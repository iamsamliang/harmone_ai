// console.log("background.js loaded revised");

// function sendMessageToBackground(message, callback) {
//   chrome.runtime.sendMessage(message, callback);
// }

// function getCurrentTabUrl(callback) {
//   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//     var tab = tabs[0];
//     callback(tab.url);
//   });
// }

// async function startRecording(duration) {
//   try {
//     const stream = await navigator.mediaDevices.getDisplayMedia({
//       audio: true,
//     });
//     console.log("Recording started");

//     const audioContext = new AudioContext();
//     const source = audioContext.createMediaStreamSource(stream);
//     source.connect(audioContext.destination);

//     // Stop the recording after 'duration' milliseconds
//     setTimeout(() => {
//       stream.getTracks().forEach((track) => track.stop());
//       audioContext.close();
//       console.log("Recording stopped");
//     }, duration);
//   } catch (error) {
//     console.error("Error starting recording:", error.message);
//   }
// }

// chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
//   if (request.message === "get_url") {
//     getCurrentTabUrl(sendResponse);
//     return true; // Keeps the message channel open for sendResponse.
//   }
// });

// function sendMessage(message) {
//   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//     chrome.tabs.sendMessage(tabs[0].id, {
//       type: "notifications",
//       data: message,
//     });
//   });
// }

// chrome.runtime.onMessage.addListener(async function (
//   message,
//   sender,
//   sendResponse
// ) {
//   if (message.type === "current_time") {
//     console.log("Received current time: " + message.currentTime);
//     chrome.storage.local.set({ currentTime: message.currentTime });
//   }
//   if (message.type === "counter") {
//     console.log("received, sending to content.js");
//     sendMessage(message.data);
//   }
//   if (message.type === "record") {
//     console.log("Sending recording request to content script");
//     chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//       console.log("sending message to content.js to record")
//       chrome.tabs.sendMessage(tabs[0].id, { type: "startRecording" });
//     });
//   }
// });

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'record' && message.data === 'start') {
      console.log('Starting recording...');
      // Send message to content script to start recording
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'startRecording' });
      });
  }
  if (message.action === "getClientId") {
      // Asynchronously fetch the clientId from storage
      chrome.storage.local.get(['client_id'], function(result) {
          let clientId = result.client_id;
          if (!clientId) {
              // ClientId not found, generate a new one
              clientId = generateClientId(); // Ensure you have this function defined to generate a clientId
              chrome.storage.local.set({'client_id': clientId}, function() {
                  // After saving the new clientId, send it as a response
                  sendResponse({ clientId: clientId });
              });
          } else {
              // ClientId found, send it as a response
              sendResponse({ clientId: clientId });
          }
      });
      return true; // Return true to indicate that you wish to send a response asynchronously
  }
});

// Listen for tab updates (like navigating to a different video)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.url && tab.url.includes("youtube.com")) {
    // If the tab updates and is still on YouTube, do nothing
  } else {
    // If the tab navigates away from YouTube, notify content script
    chrome.tabs.sendMessage(tabId, { action: 'closeWebSocket' });
  }
});

// Listen for tab removal (like closing the tab)
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  // Notify the content script in the removed tab to close WebSocket
  chrome.tabs.sendMessage(tabId, { action: 'closeWebSocket' });
});

function generateClientId() {
    // This generates a version 4 UUID.
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

function main () {

}
main()