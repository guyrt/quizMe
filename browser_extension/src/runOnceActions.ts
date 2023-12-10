/// Startup scripts to load and send DOM. NOTE! this may run too early. So far so good I think
/// but if it happens then you'll need a deferral mechanism. Or give up and just send the DOM when
/// you make your quiz?

import { DomShape } from "./interfaces";

chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action == 'fa_accessDOM') {
        const data : DomShape = {
            dom: document.body.innerHTML.toString(),
            url: document.location,
            recordTime: new Date().getTime(),
            title: document.title,
            clientIsArticle: getIsArticle()
        }
        sendResponse(data);
    }
})

function getIsArticle() : boolean {
    return document.querySelector('article') !== null;
}