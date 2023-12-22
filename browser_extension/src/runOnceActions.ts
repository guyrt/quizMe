/// Startup scripts to load and send DOM. NOTE! this may run too early. So far so good I think
/// but if it happens then you'll need a deferral mechanism. Or give up and just send the DOM when
/// you make your quiz?

import { classifyPage } from "./articleDetector";
import { DomShape } from "./interfaces";

// Fires only when a new page is loaded.
chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action == 'fa_accessDOM') {
        const data : DomShape = {
            dom: document.body.innerHTML.toString(),
            url: document.location,
            recordTime: new Date().getTime(),
            title: document.title,
            domClassification: classifyPage(document.location)
        }
        sendResponse(data);
    }
})
