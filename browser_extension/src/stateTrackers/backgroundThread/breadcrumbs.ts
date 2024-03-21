import { BasicError, BreadcrumbResponse, isBasicError } from "../../interfaces";
import { BreadcrumbsWebInterface } from "./webInterface";

export class BreadcrumbsStateHandler {
    
    private static instance: BreadcrumbsStateHandler;
    private storageEngine = chrome.storage.session;
    
    private constructor() {
        // Initialization code here
    }

    public static getInstance(): BreadcrumbsStateHandler {
        if (!BreadcrumbsStateHandler.instance) {
            BreadcrumbsStateHandler.instance = new BreadcrumbsStateHandler();
        }
        return BreadcrumbsStateHandler.instance;
    }

    public async getBreadcrumbs(pageId : string) {
        const storageKey = this.makeKey(pageId);
        const storeResults = (await this.storageEngine.get(storageKey))[storageKey];
        if (storeResults != undefined) {
            return storeResults;
        }

        return await this.getAndSet(pageId);
    }

    private async getAndSet(pageId : string) : Promise<BreadcrumbResponse | BasicError> {
        const web = new BreadcrumbsWebInterface();
        const result = await web.getBreadcrumbsPolling(pageId);
        if (!isBasicError(result)) {
            const storageKey = this.makeKey(pageId);
            this.storageEngine.set({[storageKey]: result})
        }
        return result;
    }

    private makeKey(tabId : string | number) : string {
        return `${this.keyPrefix}.${tabId}`;
    }

    private keyPrefix = "breadcrumbs";
}
