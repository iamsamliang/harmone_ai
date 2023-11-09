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


function saveToStorage(key, value) {
    let items = {};
    items[key] = value;
    chrome.storage.session.set(items, function() {
      if (chrome.runtime.lastError) {
        console.error("Error setting item in storage:", chrome.runtime.lastError.message);
      } else {
        console.log(`Item saved in storage: ${key} = ${value}`);
      }
    });
  }


  saveToStorage("testKey", "testValue");
