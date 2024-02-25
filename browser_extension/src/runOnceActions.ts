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
            showHint(true);
        }

        sendResponse(data);
    } else if (request.action === "fa_noAPIToken") {
        showHint(false);
    }
})


function showHint(isArticle : boolean) {
    const circle = document.createElement('div');
    
    // Style the circle
    circle.style.width = '28px';
    circle.style.height = '28px';
    circle.style.borderRadius = '50%';
    circle.style.position = 'fixed';
    circle.style.top = '20px';
    circle.style.right = '20px';
    circle.style.zIndex = '1000';
    circle.style.alignItems = 'center';
    circle.style.justifyContent = 'center';
    circle.style.display = 'flex';
    circle.style.fontSize = '11px';
    circle.style.cursor = 'pointer';
    circle.style.fontWeight = '800'

    circle.innerText = "We!";

    // Add animation for fading out
    circle.style.transition = 'opacity 15s ease-in-out';
    
    if (isArticle) {
        styleToHint(circle);
    } else {
        styleToLogin(circle);
    }
    
    // Append the circle to the body
    document.body.appendChild(circle);

    //Set a timeout to fade the circle out after 15 seconds
    setTimeout(() => {
        circle.style.opacity = '0';
        
        // Remove the circle from the DOM after it's fully faded out
        setTimeout(() => circle.remove(), 15000); // Ensure this matches the transition time
    }, 50000); // Start fading immediately; adjust this delay as needed
}

const yellow = "#FFCC00";
const blue = "#4741de";

function styleToLogin(circle : HTMLDivElement) {
    circle.style.color = blue;
    circle.style.backgroundColor = yellow;
    circle.style.border = `2px solid ${blue}`;
    circle.title = "Let's get you logged in.";

    circle.onclick = () => {
        chrome.runtime.sendMessage({action: 'fa_onLoginReminderClick'});
    };
}


function styleToHint(circle : HTMLDivElement) {
    circle.style.backgroundColor = blue;
    circle.style.color = yellow;
    circle.style.border = `2px solid ${yellow}`;
    circle.title = "Get the point!";

    circle.onclick = () => {
        chrome.runtime.sendMessage({action: 'fa_onReminderClick', payload: {url: document.location.href}});
    };
}