/**
 * Finite State Machine that stores state for any tab on the side panel.
 * 
 * State is defined per tab.
 * 
 * Finite State Machine lives in the SidePanel context.
 */

import { SinglePageDetailsChangeMessage, SinglePageDetails, ChromeMessage } from "../interfaces";


export type SidePanelState = "PageNotUploaded" | "PageUploadedAndClassified" | "UploadError" | "ActiveQuizShowing" | "ShowStats" | "UserLoggedOut"


class SidePanelFiniteStateMachine {

    private activeTabId : number = -1;

    private state : SidePanelState = "PageNotUploaded"

    private listeners: ((state: SidePanelState) => void)[] = [];

    public getState() : SidePanelState {
        return this.state;
    }

    public subscribe(listener: (state: SidePanelState) => void): void {
        this.listeners.push(listener);
    }

    public unsubscribe(listener: (state: SidePanelState) => void): void {
        this.listeners = this.listeners.filter(l => l !== listener);
    }

    public updateState(singlePage : SinglePageDetails) {
        const sameTab = singlePage.key == this.activeTabId;
        this.activeTabId = singlePage.key;

        // todo figure out latest state.
        const currentState = this.state;

        if ((sameTab == false || currentState != this.state)) {
            this.listeners.forEach(listener => listener(this.state));
        }
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
});