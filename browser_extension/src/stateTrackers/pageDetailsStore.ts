import { SinglePageDetails } from "../interfaces";
import { log } from "../utils/logger";


type PageDetailsMap = {
    [key: number]: SinglePageDetails
}


/// Storage that wraps a local cache and chrome storage of SinglePageDetails.
class PageDetailsStore {
    private pageDetails : PageDetailsMap = {}

    public async getPageDetails(tabId : number) : Promise<SinglePageDetails | undefined> {
        if (tabId in this.pageDetails) {
            //log(`Get ${tabId} from local storage.`);
            return Promise.resolve(this.pageDetails[tabId]);
        }

        // try to return from storage
        const storageKey = this.makeKey(tabId);
        const storeResults = await chrome.storage.sync.get(storageKey);
        const v = storeResults[storageKey];
        if (v != undefined) {
            log(`Got ${tabId} from remote storage.`);
            this.pageDetails[tabId] = v;
        } else {
            log(`Tab ${tabId} not found.`)
        }

        return Promise.resolve(v);
    }

    public setPageDetails(tabId : number, page : SinglePageDetails) {
        const storageKey = this.makeKey(tabId);
        chrome.storage.sync.set({[storageKey]: page}, () => {
            log(`Set ${page.url.href} to ${storageKey}`);
        });
        this.pageDetails[tabId] = page;
    }

    public async deletePageDetails(tabId : number) {
        delete this.pageDetails[tabId];
        await chrome.storage.sync.remove(this.makeKey(tabId));
    }

    private makeKey(tabId : number) : string {
        return `singlepagedetails.${tabId}`;
    }

}


export const pageDetailsStore = new PageDetailsStore();
