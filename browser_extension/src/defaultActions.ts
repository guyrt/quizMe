import { DomShape } from "./interfaces";

console.log("Fire message: fa_pageLoaded")
chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("FA: gather page");
    if (request.action == 'fa_accessDOM') {
        const data : DomShape = {
            dom: document.body.innerHTML.toString(),
            url: document.location,
            recordTime: new Date().getTime(),
            title: document.title
        }
        sendResponse(data);
    }
})
