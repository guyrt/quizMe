import { classifyPage } from "./articleDetector";
import { DomShape } from "./interfaces";

function handleUrlChange() {
    console.log("Url change detected");
    chrome.runtime.sendMessage({action: 'fa_pageLoaded'})
}

handleUrlChange(); // on load

const observer = new MutationObserver((mutations, obs) => {
    if (window.location.href !== lastUrl) {
        lastUrl = window.location.href;
        handleUrlChange();
    }
});

const config = { childList: true, subtree: true };
const targetNode = document.body;

let lastUrl = window.location.href;
observer.observe(targetNode, config);

// This is a separate call response rather than simply sending in fa_pageLoaded b/c error pathways will also trigger calls INTO this context.
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action == 'fa_accessDOM') {
        const data : DomShape = {
            dom: document.body.innerHTML.toString(),
            url: document.location,
            recordTime: new Date().getTime(),
            title: document.title,
            domClassification: classifyPage(document.location)
        }
        sendResponse(data);
    }
})
