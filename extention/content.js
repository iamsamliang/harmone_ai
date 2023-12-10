async function main() {
    chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
        sendResponse({code: 0});
        debugger
        if (message.action === 'getSeek') {
            const video = document.querySelector('video');
            if (video && video.currentTime != null && typeof video.currentTime === 'number') {
                chrome.runtime.sendMessage({
                    action: 'getSeek',
                    data: video.currentTime
                }, response => {
                    if (chrome.runtime.lastError) {
                        console.log(chrome.runtime.lastError);
                    }
                })
            }
        }
    });
}

main()