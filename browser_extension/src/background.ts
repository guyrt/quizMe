import { ChromeMessage, DomShape } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundState";
import { log } from "./utils/logger";

console.log("Background ran");

var fa_lastActiveTab = 0;

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Check if the URL has changed
    if (changeInfo.url) {
        log(`URL changed to: ${changeInfo.url} for tab ${tabId}`);
        
        chrome.tabs.sendMessage(tabId, {action: "fa_accessDOM"}, (x) => handleFAAccessDOMMessage(tabId, x));
    }
});

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_checkIsArticle") {
        // check if the active tab is an article.
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] === undefined) {
                console.log("Unable to get active tab");
                sendResponse(false);
                return true;
            }
            const activeTabId = getActiveTabId(tabs);
            if (activeTabId == undefined) {
                console.log(`No active tab info found for tab ${activeTabId}`);
                sendResponse(false);
                return true;
            }
            const d = backgroundState.getPageDetails(activeTabId);
            console.log(`Reporting tab ${activeTabId} article status ${d?.clientIsArticle}`);
            sendResponse(d);
            return true
        });
        return true;
    }
});

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    log(`Background message received: ${message.action}`);
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
                        console.log(quiz);
                        sendResponse({
                            success: quiz != undefined,
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
    log(`Background recieved dom. TabId: ${tabId}, Url: ${response.url.href}`);
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