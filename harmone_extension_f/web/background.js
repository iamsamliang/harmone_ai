console.log('background.js loaded revised');

function sendMessageToBackground(message, callback) {
    chrome.runtime.sendMessage(message, callback);
}

function getCurrentTabUrl(callback) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var tab = tabs[0];
      callback(tab.url);
    });
}

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if(request.message === "get_url") {
            getCurrentTabUrl(sendResponse);
            return true;  // Keeps the message channel open for sendResponse.
        }
    }
);
