import { ChromeMessage, DomShape } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundState";

var cntr = 0;

console.log("Background ran");

var fa_lastActiveTab = 0;

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] === undefined) {
                return;
            }
            const tId = tabs[0].id ?? 1;
            chrome.tabs.sendMessage(
                tId, { action: "fa_accessDOM"},
                (x) => handleFAAccessDOMMessage(tId, x))
        });
    } else if (message.action === "fa_makequiz") {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

                const activeTabId = getActiveTabId(tabs);

                if (activeTabId !== undefined) {
                    backgroundState.getOrCreateAQuiz(activeTabId)
                    .then(quiz => {
                        console.log("returning a quiz");
                        sendResponse({
                            success: true,
                            quiz: quiz
                        });    
                    })
                    return true;  // indicate sending async response.
                }
                else {
                    sendResponse({
                        success: false
                    });
                }
            });
        })();
        return true;
    }
});

function handleFAAccessDOMMessage(tabId : number, response : DomShape) {
    backgroundState.uploadPage(tabId, response);
}

function getActiveTabId(tabs : chrome.tabs.Tab[]) : number | undefined{
    let activeTabId = 0;

    if (tabs.length == 0) {
        if (fa_lastActiveTab > 0) {
            activeTabId = fa_lastActiveTab;
            return activeTabId;
        }
    } else {
        const t = tabs[0].id;
        if (t !== undefined) {
            activeTabId = t;
            fa_lastActiveTab = t;
            return activeTabId;
        }
    }
    
}