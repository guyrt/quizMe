/**
 * Track changes to the DOM tree from MutationObserver.
 */
export default class DomChangeTracker {

    private lastSeenSize : number;

    private timerId : number | undefined;
    private eventuallySendId : number | undefined;

    private timerSize : number = 3000;

    public constructor() {
        this.lastSeenSize = this.getSize();
    }

    public handleMutation() {
        // if a timer has started then just bump time.
        if (this.timerId != undefined) {
            window.clearTimeout(this.timerId);
            this.timerId = window.setTimeout(this.handleTimer, this.timerSize);
        }

        const newSize = this.getSize();
        if (this.lastSeenSize == 0) {
            this.lastSeenSize = newSize;
            return;
        }

        const ratio = newSize / this.lastSeenSize;
        this.lastSeenSize = newSize;

        if (this.isBigChange(ratio)) {
            // start the timer.
            this.timerId = window.setTimeout(this.handleTimer, this.timerSize);
            this.eventuallySendId = window.setTimeout(this.handleTimer, this.timerSize * 5); // force a send eventually
        }

    }

    private handleTimer() {
        // clean up both timeouts.
        window.clearTimeout(this.eventuallySendId); 
        this.eventuallySendId = undefined;
        window.clearTimeout(this.timerId);
        this.timerId = undefined;

        chrome.runtime.sendMessage({action: 'fa_pageReloaded'})
    }

    /** doubling in size triggers. */
    private isBigChange(ratio: number) {
        return ratio > 2;
    }

    private getSize() : number {
        return document.body.innerText.length;
    }
}