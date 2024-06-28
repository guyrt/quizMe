import { ChromeMessage, QuizResponseMessage, UnknownDomain } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundThread/pageDetailsHandler";
import { PageDetailsStore } from "./stateTrackers/backgroundThread/pageDetailsStore";
import { QuizHistoryState } from "./stateTrackers/backgroundThread/quizSubscriptionState";

var fa_lastActiveTab = 0;


import TabTracker from './stateTrackers/backgroundThread/tabTimer';

import { BackgroundSharedStateWriter } from "./stateTrackers/backgroundThread/backgroundSharedStateWriter";
import { BreadcrumbsStateHandler } from "./stateTrackers/backgroundThread/breadcrumbs";


// create this - initializer will set up events.
const tabTracker = new TabTracker();

chrome.tabs.onActivated.addListener((activeInfo) => {
    // get the active tag if it exists.
    PageDetailsStore.getInstance().getPageDetails(activeInfo.tabId).then(x => {
        chrome.runtime.sendMessage({
            action: "fa_activeSinglePageDetailsChange",
            payload: x
        });
    });
});

chrome.tabs.onRemoved.addListener((tabId: number, removeInfo : chrome.tabs.TabRemoveInfo) => {
    PageDetailsStore.getInstance().deletePageDetails(tabId);
});

/* Message Listeners */
chrome.runtime.onMessage.addListener((message : QuizResponseMessage, sender, sendResponse) => {
    if (message.action === "fa_uploadQuizResult") {
        const p = (new QuizHistoryState()).uploadQuizResult(message.payload);
        p.then(x => sendResponse(x));
        return true;
    }
});


export const omnibusHandler = (message : ChromeMessage, sender : any, sendResponse : any) => {
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
            PageDetailsStore.getInstance().getPageDetails(activeTabId).then(d => {
                sendResponse(d);
            }).catch(e => {
                sendResponse({error: "nopage"});
            });
        })})();
        return true;
    } else if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        const loadedUrl = message.payload.url;
        backgroundState.handleTabUpload(loadedUrl).then(() => sendResponse());
        return true;
    } else if (message.action === "fa_pageReloaded") {
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
    } else if (message.action === "fa_getbreadcrumbs") {
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
} else if (message.action == "fa_signUserIn") {
        (new BackgroundSharedStateWriter).logUserIn(message.payload).then(x => {
            sendResponse(x);
        }).catch(x => {
            sendResponse(x);
        })
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
                    chrome.runtime.sendMessage({
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
    } else if (message.action == "fa_addNewDomainAllow") {
        const domain = message.payload.domain;

        if (domain == UnknownDomain) {
            (async () => {chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {

                if (tabs.length > 0) {
                    const tab = tabs[0];
                    const url = tab.url;
                    if (url !== undefined) {
                        try {
                            const parsedUrl = new URL(url);
                            const domain = parsedUrl.hostname;
                            (new BackgroundSharedStateWriter()).addAllowDomain(domain).then(
                                // purge background. 
                                success => {
                                    tab?.id !== undefined && PageDetailsStore.getInstance().deletePageDetails(tab.id);

                                    sendResponse({success: success})
                                }
                            ).catch(e => {
                                sendResponse({error: "error allowing domain"});
                            })
                        } catch (error) {
                            console.error('Invalid URL', error);
                            sendResponse({error: "error allowing domain"});
                        }
                    }
                } else {
                    sendResponse({error: "error allowing domain"});
                }
    
            });
            })();
        } else {
            (new BackgroundSharedStateWriter()).addAllowDomain(domain).then(
                success => sendResponse({success: success})
            ).catch(e => {
                sendResponse({error: "error allowing domain"});
            })
        }
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
    } else if (message.action == "fa_deleteDomainAllow") {
        (new BackgroundSharedStateWriter()).dropDomainAllow(message.payload.domain).then(
            domains => sendResponse({payload: domains})
        ).catch(e => {
            sendResponse({error: "error getting allowed domains"});
        })
        return true;
    } else if (message.action === "fa_setKVPSetting") {
        const key = message.payload.key;
        const value = message.payload.value;
        console.log(`Setting ${key}: ${value}`);
        (new BackgroundSharedStateWriter()).setKVPSetting(key, value);
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

