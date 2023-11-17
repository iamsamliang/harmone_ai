// background.js
console.log('background.js loaded revised');

function sendMessage(message) {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { "type": "notifications", "data": message });
  });
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.type === "current_time") {
    console.log("Received current time: " + message.currentTime);
    chrome.storage.local.set({ 'currentTime': message.currentTime });
  }
  if (message.type === "counter") {
    console.log("received");
    sendMessage(message.data);
  }
});
