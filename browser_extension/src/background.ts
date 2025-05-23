import { 
    ChromeMessage,
    isAddNewDomainAllow,
    isDeleteDomainAllowMessage,
    isGetBreadcrumbsMessage,
    isGetCurrentPageMessage,
    isPageLoadedMessage,
    isPageReloadedMessage, 
    isQuizResponseMessage, 
    isSetKVPSetting, 
    isSignUserInMessage
} from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundThread/pageDetailsHandler";
import { PageDetailsStore } from "./stateTrackers/backgroundThread/pageDetailsStore";
import { QuizHistoryState } from "./stateTrackers/backgroundThread/quizSubscriptionState";

var fa_lastActiveTab = 0;


import TabTracker from './stateTrackers/backgroundThread/tabTimer';

import { BackgroundSharedStateWriter } from "./stateTrackers/backgroundThread/backgroundSharedStateWriter";
import { BreadcrumbsStateHandler } from "./stateTrackers/backgroundThread/breadcrumbs";
import { handleAddNewDomainAllow, handleDeleteDomainAllow, handleQuizResponseMessage, setKVPSetting } from "./messagePassing/backgroundHandlers";
import { sendRuntimeMessage } from "./messagePassing/messageProxy";


// create this - initializer will set up events.
const tabTracker = new TabTracker();

chrome.tabs.onActivated.addListener((activeInfo) => {
    // get the active tag if it exists.
    PageDetailsStore.getInstance().getPageDetails(activeInfo.tabId).then(x => {
        sendRuntimeMessage({
            action: "fa_activeSinglePageDetailsChange",
            payload: x
        });
    });
});

chrome.tabs.onRemoved.addListener((tabId: number, removeInfo : chrome.tabs.TabRemoveInfo) => {
    PageDetailsStore.getInstance().deletePageDetails(tabId);
});

export const omnibusHandler = (message : ChromeMessage, sender : any, sendResponse : any) => {
    if (isGetCurrentPageMessage(message)) {
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
            PageDetailsStore.getInstance().getPageDetails(activeTabId).then(d => {
                sendResponse(d);
            }).catch(e => {
                sendResponse({error: "nopage"});
            });
        })})();
        return true;
    } else if (isPageLoadedMessage(message)) {
        // Perform action on page load
        const loadedUrl = message.payload.url;
        backgroundState.handleTabUpload(loadedUrl).then(() => sendResponse());
        return true;
    } else if (isPageReloadedMessage(message)) {
        const tId = message.payload.tabId;
        chrome.tabs.sendMessage(
            tId,
            {action: "fa_accessDOM", payload: {tabId: tId}},
            (x) => backgroundState.handleFAAccessDOMMessage(tId, x, false)
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
        const state = (new QuizHistoryState()).getLatestQuizHistory();
        state.then(x => sendResponse(x))
            .catch(x => sendResponse({error: 'quizHistoryError'}));
        return true;
    } else if (isGetBreadcrumbsMessage(message)) {
        // retrieve breadcrumbs for a page.
        console.log(`got breadcrumb request for ${message.payload.pageId}`)
        const pageId = message.payload.pageId
        const state = BreadcrumbsStateHandler.getInstance().getBreadcrumbs(pageId);
        state.then(x => sendResponse(x))
            .catch(x => sendResponse(x))
        return true;
    } else if (message.action === 'fa_onReminderClick') {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

            const activeTabId = getActiveTabId(tabs);

            if (activeTabId !== undefined) {
                chrome.sidePanel.open({tabId: activeTabId});
            }
        });
        })();
    } else if (message.action == "fa_logUserOut") {
        (new BackgroundSharedStateWriter).logUserOut();
    } else if (isSignUserInMessage(message)) {
        (new BackgroundSharedStateWriter()).logUserIn(message.payload).then(sendResponse).catch(sendResponse);
        return true;
    } else if (message.action == "fa_createNewUser") {
        (new BackgroundSharedStateWriter).signupUser(message.payload).then(x => {
            sendResponse(x);
        }).catch(x => {
            sendResponse(x);
        })
        return true;
    } else if (message.action == "fa_onLoginReminderClick") {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

            const activeTabId = getActiveTabId(tabs);

            if (activeTabId !== undefined) {
                chrome.sidePanel.open({tabId: activeTabId}).then(() => {
                    sendRuntimeMessage({
                        action: "fa_sidePanelNoAPIToken",
                        payload: {}
                    });    
                });
            }
        });
        })();
        return true;
    } else if (message.action == "fa_addNewDomainBlock") {
        const domain = message.payload.domain;
        (new BackgroundSharedStateWriter()).addDomainBlock(domain).then(
            success => sendResponse({success: success})
        ).catch(e => {
            sendResponse({error: "error blocking domain"});
        })
        return true;
    } else if (isAddNewDomainAllow(message)) {
        (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {
                const activeTabId = getActiveTabId(tabs);
                activeTabId !== undefined && handleAddNewDomainAllow(message, activeTabId, sendResponse);
            });
        })();
        return true;
    } else if (message.action == "fa_loadBlockedDomains") {
        (new BackgroundSharedStateWriter()).loadDomainBlockList().then(
            domains => sendResponse({payload: domains})
        ).catch(e => {
            sendResponse({error: "error getting blocked domains"});
        })
        return true;
    } else if (message.action == "fa_loadAllowedDomains") {
        (new BackgroundSharedStateWriter()).loadDomainAllowList().then(
            domains => sendResponse({payload: domains})
        ).catch(e => {
            sendResponse({error: "error getting blocked domains"});
        })
        return true;
    } else if (message.action == "fa_deleteDomainBlock") {
        (new BackgroundSharedStateWriter()).dropDomainBlock(message.payload.domain).then(
            domains => sendResponse({payload: domains})
        ).catch(e => {
            sendResponse({error: "error getting blocked domains"});
        })
        return true;
    } else if (isDeleteDomainAllowMessage(message)) {
        handleDeleteDomainAllow(message, sendResponse)
    } else if (isSetKVPSetting(message)) {
        setKVPSetting(message);
    } else if (isQuizResponseMessage(message)) {
        (async () => {
            await handleQuizResponseMessage(message, sendResponse)
        })();
        return true;
    }
}

chrome.runtime.onMessage.addListener(omnibusHandler);

// @ts-ignore
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error : any) => console.error(error));


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

