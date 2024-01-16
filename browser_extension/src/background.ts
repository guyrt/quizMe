import { ChromeMessage, DomShape, QuizResponseMessage } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundThread/backgroundState";
import { pageDetailsStore } from "./stateTrackers/backgroundThread/pageDetailsStore";
import { quizHistoryState } from "./stateTrackers/backgroundThread/quizSubscriptionState";
import { log } from "./utils/logger";
import { uploadQuizResults } from "./webInterface";

console.log("Background ran");

var fa_lastActiveTab = 0;


chrome.tabs.onActivated.addListener((activeInfo) => {
    // get the active tag if it exists.
    console.log(`Change tab to ${activeInfo.tabId}`);
    pageDetailsStore.getPageDetails(activeInfo.tabId).then(x => {
        chrome.runtime.sendMessage({
            action: "fa_activeSinglePageDetailsChange",
            payload: x ? x : {error: 'no page exists'}
        });
    });
});

chrome.tabs.onRemoved.addListener((tabId: number, removeInfo : chrome.tabs.TabRemoveInfo) => {
    pageDetailsStore.deletePageDetails(tabId);
});

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_getCurrentPage") {
        // check if the active tab is an article.
        (async () => {chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            log("start query");
            if (!tabs.length) {
                console.log("Unable to get active tab");
                sendResponse({error: "no active tab"});
                return true;
            }
            const activeTabId = getActiveTabId(tabs);
            if (activeTabId == undefined) {
                console.log(`No active tab info found for tab ${activeTabId}`);
                sendResponse({error: `No active tab info for tab ${activeTabId}`});
                return true;
            }
            pageDetailsStore.getPageDetails(activeTabId).then(d => {
                console.log(`Reporting tab ${activeTabId} article status ${d?.domClassification?.classification}`);
                sendResponse(d ? d : {error: "no details returned"});
            }).catch(e => {
                sendResponse({error: e.message});
            });
            return true;
        })})();
        return true;
    }
    return false;
});

chrome.runtime.onMessage.addListener((message : QuizResponseMessage, sender, sendResponse) => {
    if (message.action === "fa_uploadQuizResult") {
        console.log("Upload quiz response to server");
        uploadQuizResults(message.payload);
    }
});


chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        (async () => {
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (tabs[0] === undefined) {
                    return;
                }
                const tId = tabs[0].id ?? 1;
                chrome.tabs.sendMessage(
                    tId, { action: "fa_accessDOM"},
                    (x) => handleFAAccessDOMMessage(tId, x))
            })
        })();
    } else if (message.action === "fa_makequiz") {
        (async () => {
            chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

                const activeTabId = getActiveTabId(tabs);

                if (activeTabId !== undefined) {
                    backgroundState.getOrCreateAQuiz(activeTabId, message.payload['forceReload'] ?? false)
                }
            });
        })();
        return false;
    } else if (message.action === "fa_getQuizHistory") {
        // Update the quiz history and return it
        (async () => {
            const state = await quizHistoryState.getLatestQuizHistory();
            sendResponse(state);
        })();
        return true;
    }
});


// @ts-ignore
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error : any) => console.error(error));


function handleFAAccessDOMMessage(tabId : number, response : DomShape) {
    log(`Background received dom. TabId: ${tabId}, Url: ${response?.url.href}`);
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