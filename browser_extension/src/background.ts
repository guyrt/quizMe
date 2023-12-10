import { ChromeMessage, DomShape } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundState";

var cntr = 0;

console.log("Background ran");

chrome.runtime.onMessage.addListener(async (message : ChromeMessage, sender, sendResponse) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0] === undefined) {
                return;
            }
            const tId = tabs[0].id ?? 1;
            const requestId = `r${cntr++}${new Date().getTime()}`
            chrome.tabs.sendMessage(tId, { action: "fa_accessDOM", requestId : requestId }, handleFAAccessDOMMessage)
        });
    } else if (message.action === "fa_makequiz") {
        chrome.tabs.query({ active: true, currentWindow: true }, async function(tabs) {
            // tabs[0] is the active tab in the current window
            let activeTab = tabs[0];
        
            const key = activeTab.url ?? "";
            const quiz = await backgroundState.getOrCreateAQuiz(key);
            sendResponse(quiz);

            // You can now use activeTab as needed
        });

    }
});

function handleFAAccessDOMMessage(response : DomShape) {
    backgroundState.uploadPage(response);
}
