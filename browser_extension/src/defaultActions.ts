import { DomShape } from "./interfaces";

chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded");
})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
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
