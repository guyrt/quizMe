import { classifyPage } from "./articleDetector";
import DomChangeTracker from "./domAccessLayer/domChangeTracker";
import { getReaderMode, getCleanDom } from "./domAccessLayer/readerModeExtract";
import { DomShape } from "./interfaces";

function handleUrlChange() {
    chrome.runtime.sendMessage({action: 'fa_pageLoaded', payload: {url: document.location.href}});

}

handleUrlChange(); // on load

const domChangeTracker = new DomChangeTracker();

const observer = new MutationObserver((mutations, obs) => {
    if (window.location.href !== lastUrl) {
        lastUrl = window.location.href;
        handleUrlChange();
        return;
    }
    
    // default handler: set a timer. if it's been 'long enough' then check 
    // if you've gotten a big change to innertext. if yes then set a timer and re-send
    // when it calms down.
    
    // handle resubmit as a different thing b/c you want to overwrite the back end 
    // i think. maybe a new layer of model - URL/PageView/Capture
    domChangeTracker.handleMutation();
});

const config = { childList: true, subtree: true };
const targetNode = document.body;

let lastUrl = window.location.href;
observer.observe(targetNode, config);

// This is a separate call response rather than simply sending in fa_pageLoaded b/c error pathways will also trigger calls INTO this context.
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action == 'fa_accessDOM') {
        const tabId = request.payload.tabId;
        domChangeTracker.setTabId(tabId);
        const readerMode = getReaderMode(document);
        
        const data : DomShape = {
            dom: getCleanDom(document).body.innerHTML.toString(),
            url: document.location,
            recordTime: Math.floor((new Date()).getTime() / 100),  // 0.1 second resolution.
            title: readerMode?.title ?? document.title,
            byline : readerMode?.byline ?? "",
            domClassification: classifyPage(document.location),
            readerContent: readerMode?.content ?? "",
            siteName : readerMode?.siteName ?? "",
            publishedTime : readerMode?.publishedTime ?? ""
        }

        if (data.domClassification.classification == "article") {
            showCircle();
        }

        sendResponse(data);
    }
})


function showCircle() {
    const circle = document.createElement('div');
    
    // Style the circle
    circle.style.width = '25px';
    circle.style.height = '25px';
    circle.style.backgroundColor = '#4741de';
    circle.style.borderRadius = '50%';
    circle.style.position = 'fixed';
    circle.style.top = '20px';
    circle.style.right = '20px';
    circle.style.zIndex = '1000';
    
    // Add animation for fading out
    circle.style.transition = 'opacity 15s ease-in-out';
    
    // Append the circle to the body
    document.body.appendChild(circle);

    circle.onclick = () => {
        chrome.runtime.sendMessage({action: 'fa_onReminderClick', payload: {url: document.location.href}});
    };
    
    // Set a timeout to fade the circle out after 15 seconds
    setTimeout(() => {
        circle.style.opacity = '0';
        
        // Remove the circle from the DOM after it's fully faded out
        setTimeout(() => circle.remove(), 15000); // Ensure this matches the transition time
    }, 50000); // Start fading immediately; adjust this delay as needed
}

