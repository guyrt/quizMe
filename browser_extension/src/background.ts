import { DomShape } from "./interfaces";
import {backgroundState} from "./stateTrackers/backgroundState";

var cntr = 0;

chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const tId = tabs[0]?.id ?? 1;
            const requestId = `r${cntr++}${new Date().getTime()}`
            chrome.tabs.sendMessage(tId, { action: "fa_accessDOM", requestId : requestId }, handleFAAccessDOMMessage)
        });
    }
});

function handleFAAccessDOMMessage(response : DomShape) {
    backgroundState.uploadPage(response);
}
