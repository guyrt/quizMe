import { DomShape } from "./interfaces";
import {state} from "./appState";

chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.action === "fa_pageLoaded") {
        // Perform action on page load
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const tId = tabs[0].id ?? 1;
            chrome.tabs.sendMessage(tId, { action: "fa_accessDOM" }, handleFAAccessDOMMessage)
        });
    }
});


function handleFAAccessDOMMessage(response : DomShape) {
    console.log(response.url);
    state.uploadPage(response);
}
