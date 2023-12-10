import { ChromeMessage, DomShape } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundState";

var cntr = 0;

console.log("Background ran");

var fa_lastActiveTab = 0;

chrome.runtime.onMessage.addListener(async (message : ChromeMessage, sender, sendResponse) => {
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
        chrome.tabs.query({ active: true, lastFocusedWindow: true }, async function(tabs) {

            let activeTabId = 0;

            let noTabId = false;

            if (tabs.length == 0) {
                if (fa_lastActiveTab > 0) {
                    activeTabId = fa_lastActiveTab;
                    noTabId = false;
                } else {
                    noTabId = true;
                }
            } else {
                const t = tabs[0].id;
                if (t === undefined) {
                    noTabId = true;
                } else {
                    activeTabId = t;
                    fa_lastActiveTab = t;
                }
            }

            if (!noTabId) {
                const quiz = await backgroundState.getOrCreateAQuiz(activeTabId);
                sendResponse({
                    success: true,
                    quiz: quiz
                });
            }
            else {
                sendResponse({
                    success: false,
                    quiz: undefined
                });
            }
        });

    }
});

function handleFAAccessDOMMessage(tabId : number, response : DomShape) {
    backgroundState.uploadPage(tabId, response);
}
