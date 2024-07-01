/// Always use this to send messages.

import { ChromeMessage } from "../interfaces";

export function sendRuntimeMessage(message : ChromeMessage, callback? : (response : any) => void) : void {
    console.log(`Sending message ${message.action}`);
    if (callback === undefined) {
        chrome.runtime.sendMessage(message);
    } else {
        chrome.runtime.sendMessage(message, callback);
    }
}
