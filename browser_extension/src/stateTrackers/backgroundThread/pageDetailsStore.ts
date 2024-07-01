import { MaybeSinglePageDetails, isSinglePageDetails } from "../../interfaces";
import { sendRuntimeMessage } from "../../messagePassing/messageProxy";


type PageDetailsMap = {
    [key: number]: MaybeSinglePageDetails
}


/// Storage that wraps a local cache and chrome storage of SinglePageDetails.
export class PageDetailsStore {

    private static instance: PageDetailsStore;
    private storageEngine = chrome.storage.local;

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
        const storeResults = await this.storageEngine.get(storageKey);
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
        this.storageEngine.set({[storageKey]: page}, () => {});
        this.pageDetails[tabId] = page;
        if (broadcast) {
            console.log(`Sending message activeSinglePageDetailsChange with`, page);
            sendRuntimeMessage({action: "fa_activeSinglePageDetailsChange", payload: page});
        }
    }

    /**
     * Delete all pages that match a domain.
     * @param domain 
     */
    public async deletePagesWithDomain(domain : string) {
        for (const key in this.pageDetails) {
            const value = this.pageDetails[key];
            if (isSinglePageDetails(value)) {
                if (value.url.host.endsWith(domain)) {  // should be ends with to handle subdomain
                    delete this.pageDetails[key];
                }
            }
        }

        const allKeys = await this.storageEngine.get();
        for (const key in allKeys) {
            if (key.startsWith(this.keyPrefix)) {
                const value = allKeys[key];
                if (isSinglePageDetails(value) && value.url.host.endsWith(domain)) {
                    await this.storageEngine.remove(key);
                }
            }
        }
    }

    public async deletePageDetails(tabId : number) {
        delete this.pageDetails[tabId];
        await this.storageEngine.remove(this.makeKey(tabId));
    }

    public async deleteAllPageDetails() {
        const kPrefix = this.keyPrefix;
        this.storageEngine.get(null, (items) => {
            const keysToDelete = Object.keys(items).filter(key => key.startsWith(kPrefix));
            this.storageEngine.remove(keysToDelete);
        });
        this.pageDetails = {};
    }

    private makeKey(tabId : number | string) : string {
        return `${this.keyPrefix}.${tabId}`;
    }

    private keyPrefix = "singlepagedetails"

}
