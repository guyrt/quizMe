/**
 * Finite State Machine that stores state for any tab on the side panel.
 * 
 * State is defined per tab.
 * 
 * Finite State Machine lives in the SidePanel context.
 */

import { SinglePageDetailsChangeMessage, SinglePageDetails, ChromeMessage } from "../../interfaces";
import { sharedState } from "../sharedState";


export type SidePanelState = "PageNotUploaded" 
| "PageUploadedAndClassified" 
| "UploadError" 
| "UserLoggedOut" 
| "ShowUserSettings" 
| "PageBlocked" 
| "Reload"  // not an error so don't apologize.
;


class SidePanelFiniteStateMachine {

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

    public updateReload() {
        if (this.state == 'Reload') {
            return;
        }
        this.state = 'Reload'
        this.publish();
    }

    public async updateState(singlePage : SinglePageDetails) {
        if (this.state == "UserLoggedOut") {
            // check for a token
            if (!await sharedState.hasApiToken()) {
                return;
            }
        }

        this.activeDetails = singlePage;

        if (singlePage.uploadState == "inprogress" || singlePage.uploadState == "notstarted") {
            this.state = "PageNotUploaded";
        } else if (singlePage.uploadState == "error") {
            this.state = "UploadError";
        } else if (singlePage.uploadState == "completed") {
            this.state = "PageUploadedAndClassified";
        } else if (singlePage.uploadState == "donotprocess") {
            this.state = "PageBlocked";
        } else {
            Error(`Unexpected state ${singlePage.uploadState}`);
        }

        this.publish();
    }

    public async triggerCheck() {
        console.log("Trigger check");

        if (await sharedState.getApiToken() == undefined) {
            this.handleUserLoggedOut();
        }

        // get the latest state then trigger.
        // step 1: get latest state from BE
        chrome.runtime.sendMessage({ action: "fa_getCurrentPage", payload: {} }, (_domFacts: SinglePageDetails | { error: string }) => {
            // Check if the response contains an error
            console.log("FSM trigger check callback");
            if (_domFacts == undefined) {
                return;
            } else if ('error' in _domFacts) {
                this.updateReload();
                console.log(`FSM got error: ${_domFacts.error}`);
            } else {
                // Call updateState with the received data
                console.log("FSM updaing from trigger check")
                this.updateState(_domFacts);
            }
        });
        
    }

    public handleUserLoggedOut() {
        if (this.state != "UserLoggedOut") {
            this.state = "UserLoggedOut";
            this.publish();
        }
    }

    public setShowOptions() {
        this.state = "ShowUserSettings";
        this.publish();
    }

    private publish() {
        console.log(`Reacting to state ${this.state}`);
        this.listeners.forEach(listener => {
            listener(this.state)
        });
    }

}

export const fsm = new SidePanelFiniteStateMachine();

// Listen for one Message: active details changed.
chrome.runtime.onMessage.addListener((message : SinglePageDetailsChangeMessage, sender) => {
    if (message.action === "fa_activeSinglePageDetailsChange") {
        if ('error' in message.payload && message.payload.error == "no page exists") {
            fsm.updateReload();
        } else {
            fsm.updateState(message.payload as SinglePageDetails);
        }
        return true;
    }
    return false;
});

chrome.runtime.onMessage.addListener((message : ChromeMessage, sender) => {
    if (message.action === "fa_noAPIToken") {
        fsm.handleUserLoggedOut();
    }
    return true;
});