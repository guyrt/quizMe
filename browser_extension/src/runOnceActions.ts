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

        if (data.domClassification.classification == "article") {
            showCircle();
        }

        sendResponse(data);
    }
})


function showCircle() {
    const circle = document.createElement('div');
    
    // Style the circle
    circle.style.width = '50px';
    circle.style.height = '50px';
    circle.style.backgroundColor = 'purple';
    circle.style.borderRadius = '50%';
    circle.style.position = 'fixed';
    circle.style.top = '20px';
    circle.style.right = '20px';
    circle.style.zIndex = '1000';
    
    // Add animation for fading out
    circle.style.transition = 'opacity 15s ease-in-out';
    
    // Append the circle to the body
    document.body.appendChild(circle);
    
    // Set a timeout to fade the circle out after 15 seconds
    setTimeout(() => {
        circle.style.opacity = '0';
        
        // Remove the circle from the DOM after it's fully faded out
        setTimeout(() => circle.remove(), 15000); // Ensure this matches the transition time
    }, 50000); // Start fading immediately; adjust this delay as needed
}