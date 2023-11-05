self.onmessage = function(event) {
    const { message, sender, sendResponse } = event.data;
    if (message === "get_url") {
      chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        const tab = tabs[0];
        sendResponse(tab.url);
      });
      return true;  // Keeps the message channel open for sendResponse.
    }
  };
  
  self.onconnect = function(connectEvent) {
    connectEvent.ports[0].onmessage = self.onmessage;
  };
  

  