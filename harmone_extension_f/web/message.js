console.log('messaging.js loaded');

function sendMessageToBackground(message, callback) {
    console.log('sendMessageToBackground called with message:', message);
    chrome.runtime.sendMessage(message, function(response) {
        console.log('Received response:', response);
        callback(response);
    });
}
