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
        const storeResults = await this.storageEngine.get(storageKey);
        const v = storeResults[storageKey];
        if (v != undefined) {
            return v
        }
    }

    private async getAndSet(pageId : string) {
        
    }

    private makeKey(tabId : string | number) : string {
        return `${this.keyPrefix}.${tabId}`;
    }

    private keyPrefix = "breadcrumbs";
}