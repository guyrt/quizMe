chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded");
})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log(request.action);
    sendResponse({uri: document.documentURI, body: document.body.innerHTML});
})
