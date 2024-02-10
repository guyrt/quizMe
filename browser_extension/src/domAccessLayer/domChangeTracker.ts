/**
 * Track changes to the DOM tree from MutationObserver.
 */
export default class DomChangeTracker {

    private lastSeenSize : number;

    private timerIds : number[];
    private timerSize : number = 3000;
    private tabId : number | undefined;

    public constructor() {
        this.lastSeenSize = this.getSize();
        this.timerIds = [];
    }

    public setTabId(tabId : number) {
        this.tabId = tabId;
    }

    public handleMutation() {
        const newSize = this.getSize();
        if (this.lastSeenSize == 0) {
            this.lastSeenSize = newSize;
            return;
        }

        const ratio = newSize / this.lastSeenSize;

        if (this.isBigChange(ratio)) {
            console.log(`Big change from ${this.lastSeenSize} to ${newSize}`);

            // if a timer has started then just bump time.
            if (this.timerIds.length > 0) {
                this.clearIds();
                this.timerIds.push(window.setTimeout(() => this.handleTimer(), this.timerSize));
            } else {
                this.timerIds.push(window.setTimeout(() => this.handleTimer(), this.timerSize));
                this.timerIds.push(window.setTimeout(() => this.handleTimer(), this.timerSize * 5)); // force a send eventually
            }
        }
        this.lastSeenSize = newSize;
    }

    private clearIds() {
        this.timerIds.map(x => window.clearTimeout(x));
        this.timerIds = [];
    }

    private handleTimer() {
        // clean up both timeouts.
        if (this.tabId == undefined) {
            return;  // let a later one come along (if our fallback exists...)
        }
        this.clearIds();
        console.log("Change fired");
        chrome.runtime.sendMessage({action: 'fa_pageReloaded', payload: {tabId: this.tabId}});
    }

    /** doubling in size triggers. */
    private isBigChange(ratio: number) {
        return ratio > 2;
    }

    private getSize() : number {
        return document.body.innerText.length;
    }
}