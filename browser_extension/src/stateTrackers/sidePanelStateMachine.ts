/**
 * Finite State Machine that stores state for any tab on the side panel.
 * 
 * State is defined per tab.
 * 
 * Finite State Machine lives in the SidePanel context.
 */

import { SinglePageDetailsChangeMessage, SinglePageDetails, ChromeMessage } from "../interfaces";
import { log } from "../utils/logger";


export type SidePanelState = "PageNotUploaded" | "PageUploadedAndClassified" | "UploadError" | "UserLoggedOut" | "QuizBeingDeveloped"


class SidePanelFiniteStateMachine {

    private activeTabId : number = -1;

    private activeDetails : SinglePageDetails | undefined = undefined;

    private state : SidePanelState = "PageNotUploaded"

    private listeners: ((state: SidePanelState) => void)[] = [];

    public getState() : SidePanelState {
        return this.state;
    }

    public getActiveDetails() : SinglePageDetails | undefined {
        return this.activeDetails;
    }

    public subscribe(listener: (state: SidePanelState) => void): void {
        this.listeners.push(listener);
    }

    public unsubscribe(listener: (state: SidePanelState) => void): void {
        this.listeners = this.listeners.filter(l => l !== listener);
    }

    /**
     * Store quiz being built state. Note that this isn't persistant by design. Any change below will overwrite.
     * Not sure this is good enough but let's try for now.
     */
    public setQuizBeingBuilt() {
        this.state = "QuizBeingDeveloped";
        this.listeners.forEach(listener => listener(this.state));
    }

    public updateState(singlePage : SinglePageDetails) {
        if (singlePage != undefined) {
            log(`Updating state ${singlePage.uploadState} for ${singlePage.url.href}`);

            this.activeTabId = singlePage.key;
            this.activeDetails = singlePage;

            if (singlePage.uploadState == "inprogress" || singlePage.uploadState == "notstarted") {
                this.state = "PageNotUploaded";
            } else if (singlePage.uploadState == "error") {
                this.state = "UploadError";
            } else if (singlePage.uploadState == "completed") {
                this.state = "PageUploadedAndClassified";
            } else {
                Error(`Unexpected state ${singlePage.uploadState}`);
            }
        } else {
            console.log(`Updating state with empty page.`);
            this.state = "UploadError";
        }

        this.listeners.forEach(listener => {
            console.log("calling listener");
            listener(this.state)
        });
    }

    public triggerCheck() {
        // get the latest state then trigger.
        // step 1: get latest state from BE
        chrome.runtime.sendMessage({action: "fa_checkIsArticle", payload: {}}).then((_domFacts : SinglePageDetails) => {
            // step 2: call updateState.
            this.updateState(_domFacts);
        });
    }

    public handleUserLoggedOut() {
        this.state = "UserLoggedOut";
        this.listeners.forEach(listener => listener(this.state));
    }

}

export const fsm = new SidePanelFiniteStateMachine();

// Listen for one Message: active details changed.
chrome.runtime.onMessage.addListener((message : SinglePageDetailsChangeMessage, sender) => {
    if (message.action === "fa_activeSinglePageDetailsChange") {
        fsm.updateState(message.payload);
    }
});

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender) => {
    if (message.action === "fa_noAPIToken") {
        fsm.handleUserLoggedOut();
    }
    return true;
});