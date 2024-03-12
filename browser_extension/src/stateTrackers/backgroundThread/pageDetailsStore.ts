import { MaybeSinglePageDetails } from "../../interfaces";


type PageDetailsMap = {
    [key: number]: MaybeSinglePageDetails
}


const storageEngine = chrome.storage.local;


/// Storage that wraps a local cache and chrome storage of SinglePageDetails.
export class PageDetailsStore {

    private static instance: PageDetailsStore;

    private pageDetails : PageDetailsMap = {}

    private constructor() {
        // Initialization code here
    }

    public static getInstance(): PageDetailsStore {
        if (!PageDetailsStore.instance) {
            PageDetailsStore.instance = new PageDetailsStore();
        }
        return PageDetailsStore.instance;
    }

    public async getPageDetails(tabId : number) : Promise<MaybeSinglePageDetails> {
        if (tabId in this.pageDetails) {
            return this.pageDetails[tabId];
        }

        // try to return from storage
        const storageKey = this.makeKey(tabId);
        const storeResults = await storageEngine.get(storageKey);
        const v = storeResults[storageKey];
        if (v != undefined) {
            this.pageDetails[tabId] = v;
            return v
        }
        return {error: 'cachemiss'};
    }

    /**
     * 
     * @param tabId 
     * @param page 
     * @param broadcast Only set to true if you are the current active tab.
     */
    public setPageDetails(tabId : number, page : MaybeSinglePageDetails, broadcast : boolean = true) {
        const storageKey = this.makeKey(tabId);
        storageEngine.set({[storageKey]: page}, () => {});
        this.pageDetails[tabId] = page;
        if (broadcast) {
            console.log(`Sending message activeSinglePageDetailsChange with`, page);
            chrome.runtime.sendMessage({action: "fa_activeSinglePageDetailsChange", payload: page});
        }
    }

    public async deletePageDetails(tabId : number) {
        delete this.pageDetails[tabId];
        await storageEngine.remove(this.makeKey(tabId));
    }

    public async deleteAllPageDetails() {
        const kPrefix = this.keyPrefix;
        storageEngine.get(null, function(items) {
            const keysToDelete = Object.keys(items).filter(key => key.startsWith(kPrefix));
            storageEngine.remove(keysToDelete);
        });
        this.pageDetails = {};
    }

    private makeKey(tabId : number | string) : string {
        return `${this.keyPrefix}.${tabId}`;
    }

    private keyPrefix = "singlepagedetails"

}
