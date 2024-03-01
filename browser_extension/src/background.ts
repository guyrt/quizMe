import { ChromeMessage, DomShape, QuizResponseMessage } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundThread/backgroundState";
import { pageDetailsStore } from "./stateTrackers/backgroundThread/pageDetailsStore";
import { quizHistoryState } from "./stateTrackers/backgroundThread/quizSubscriptionState";
import { uploadQuizResults } from "./webInterface";

var fa_lastActiveTab = 0;


const oldLogger = console.log;
console.log = () => {};


import TabTracker from './stateTrackers/backgroundThread/tabTimer';
import { SharedStateWriters } from "./stateTrackers/sharedStateWriters";

// create this - initializer will set up events.
const tabTracker = new TabTracker();

chrome.tabs.onActivated.addListener((activeInfo) => {
    // get the active tag if it exists.
    console.log(`Change tab to ${activeInfo.tabId}`);
    pageDetailsStore.getPageDetails(activeInfo.tabId).then(x => {
        chrome.runtime.sendMessage({
            action: "fa_activeSinglePageDetailsChange",
            payload: x
        });
    });
});

chrome.tabs.onRemoved.addListener((tabId: number, removeInfo : chrome.tabs.TabRemoveInfo) => {
    pageDetailsStore.deletePageDetails(tabId);
});

/* Message Listeners */
chrome.runtime.onMessage.addListener((message : QuizResponseMessage, sender, sendResponse) => {
    if (message.action === "fa_uploadQuizResult") {
        uploadQuizResults(message.payload);
    }
});


chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_getCurrentPage") {
        // check if the active tab is an article.
        (async () => {chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            
            if (!tabs.length) {
                console.log("Unable to get active tab");
                sendResponse({error: "nopage"});
                return true;
            }
            const activeTabId = getActiveTabId(tabs);
            if (activeTabId == undefined) {
                console.log(`No active tab info found for tab ${activeTabId}`);
                sendResponse({error: "nopage"});
                return true;
            }
            pageDetailsStore.getPageDetails(activeTabId).then(d => {
                sendResponse(d);
            }).catch(e => {
                sendResponse({error: "nopage"});
            });
        })})();
        return true;
    } else if (message.action === "fa_pageLoaded") {
        oldLogger(`Got action ${message.action} with ${message.payload.url}`);
        // Perform action on page load
        const loadedUrl = message.payload.url;
        (async () => {
            // handle case where we're reloading from error on current active.
            if (loadedUrl == "unknown") {
                chrome.tabs.query({currentWindow: true, active: true}, function(tabs) {
                    handleTabs(tabs, true);
                });
            } else {
                chrome.tabs.query({currentWindow: true, url: loadedUrl}, function(tabs) {
                    handleTabs(tabs, true);
                });
            }

            
        })();
    } else if (message.action === "fa_pageReloaded") {
        console.log(`Got action ${message.action}`);
        const tId = message.payload.tabId;
        chrome.tabs.sendMessage(
            tId,
            {action: "fa_accessDOM", payload: {tabId: tId}},
            (x) => handleFAAccessDOMMessage(tId, x, message.action === "fa_pageLoaded")
        );
    } else if (message.action === "fa_makequiz") {
        (async () => {
            chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

                const activeTabId = getActiveTabId(tabs);

                if (activeTabId !== undefined) {
                    const q = backgroundState.getOrCreateAQuiz(activeTabId, message.payload['forceReload'] ?? false);
                    sendResponse(q);
                } else {
                    sendResponse({'status': 'error'});
                }
            });
        })();
        return true;
    } else if (message.action === "fa_getQuizHistory") {
        // Update the quiz history and return it
        (async () => {
            const state = await quizHistoryState.getLatestQuizHistory();
            console.log("Background returning quiz history", state);
            sendResponse(state);
        })();
        return true;
    } else if (message.action === 'fa_onReminderClick') {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

            const activeTabId = getActiveTabId(tabs);

            if (activeTabId !== undefined) {
                chrome.sidePanel.open({tabId: activeTabId});
            }
        });
        })();
    } else if (message.action == "fa_userLoggedOut") {
        pageDetailsStore.deleteAllPageDetails();
    } else if (message.action == "fa_onLoginReminderClick") {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

            const activeTabId = getActiveTabId(tabs);

            if (activeTabId !== undefined) {
                chrome.sidePanel.open({tabId: activeTabId});
                chrome.runtime.sendMessage({action: "fa_noAPIToken"});
            }
        });
        })();
        return true;
    } else if (message.action == "fa_addNewDomainBlock") {
        const domain = message.payload.domain;
        (new SharedStateWriters()).addDomainBlock(domain).then(
            numRemovedPages => sendResponse({numRemovedPages: numRemovedPages})
        ).catch(e => {
            sendResponse({error: "error blocking domain"});
        })
        return true;
    } else if (message.action == "fa_loadBlockedDomains") {
        (new SharedStateWriters()).loadDomainBlockList().then(
            domains => sendResponse({payload: domains})
        ).catch(e => {
            sendResponse({error: "error getting blocked domains"});
        })
        return true;
    }
});


// @ts-ignore
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error : any) => console.error(error));


function handleTabs(tabs : chrome.tabs.Tab[], firstUpload : boolean) {
    if (tabs[0] === undefined) {
        return;
    }
    const tId = argMax<any, any>(tabs, 'lastAccessed').id;
    chrome.tabs.sendMessage(
        tId,
        {action: "fa_accessDOM", payload: {tabId: tId}},
        (x) => handleFAAccessDOMMessage(tId, x, firstUpload)
    );
}


function handleFAAccessDOMMessage(tabId : number, response : DomShape, firstUpload : boolean) {
    console.log(`Background received dom. TabId: ${tabId}, isFirst: ${firstUpload} response:`, response);
    if (firstUpload) {
        backgroundState.uploadPage(tabId, response);
    } else {
        backgroundState.uploadNewVersionSamePage(tabId, response);
    }
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

function argMax<T extends Record<K, number>, K extends keyof any>(listOfObjects: T[], key: K): T {
    const argMaxObject = listOfObjects.reduce((maxObj, currentObj) => {
      return currentObj[key] > maxObj[key] ? currentObj : maxObj;
    }, listOfObjects[0]);
    return argMaxObject;
  }