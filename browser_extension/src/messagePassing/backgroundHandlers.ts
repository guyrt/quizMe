import { AddNewDomainAllow, DeleteDomainAllowMessage, QuizResponseMessage, SetKVPSetting, UnknownDomain } from "../interfaces";
import { BackgroundSharedStateWriter } from "../stateTrackers/backgroundThread/backgroundSharedStateWriter";
import { PageDetailsStore } from "../stateTrackers/backgroundThread/pageDetailsStore";
import { QuizHistoryState } from "../stateTrackers/backgroundThread/quizSubscriptionState";

export const handleQuizResponseMessage = async (message : QuizResponseMessage, sendResponse : (response : any) => void) => {
    const quizHistory = await (new QuizHistoryState()).uploadQuizResult(message.payload);
    sendResponse(quizHistory);
}


export const setKVPSetting = (message : SetKVPSetting) => {
    const key = message.payload.key;
    const value = message.payload.value;
    (new BackgroundSharedStateWriter()).setKVPSetting(key, value);
}


export const handleDeleteDomainAllow = (message : DeleteDomainAllowMessage, sendResponse : (response : any) => void) => {
    (new BackgroundSharedStateWriter()).dropDomainAllow(message.payload.domain).then(
        domains => sendResponse({payload: domains})
    ).catch(e => {
        sendResponse({error: "error getting allowed domains"});
    })
    return true;
}

export const handleAddNewDomainAllow = (message : AddNewDomainAllow, sendResponse : (response : any) => void) => {
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
                            success => {
                                PageDetailsStore.getInstance().deletePagesWithDomain(domain).then(() => sendResponse({success: success}));
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
}