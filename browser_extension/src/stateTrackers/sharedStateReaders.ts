
export class SharedStateReaders {

    protected ApiTokenKey : string = "secret.apikey";
    protected UserEmailKey : string = "secret.email";
    protected FilterSendKey : string = "settings.filtersend";

    private domainBlockList = [
        'microsoft-my.sharepoint.com',
        'outlook.office.com', // safety check from outlook.
        'microsoft.sharepoint.com',
        'localhost',
        'totalrewards.azurefd.net',
        'statics.teams.cdn.office.net',
        'microsoft-my.sharepoint-df.com',
        'ms.portal.azure.com',
        'sapsf.com',
        'idweb.microsoft.com',
        'login.microsoftonline.com', // logins
        'digital.fidelity.com'
    ];

    public async getApiToken() : Promise<string | undefined> {
        const token = (await chrome.storage.local.get(this.ApiTokenKey))[this.ApiTokenKey];

        if (token == undefined) {
            // if a token doesn't exist, nuke local state.
            this.deleteUserState();
        }
        return token;
    }

    public async hasApiToken() {
        const token = (await chrome.storage.local.get(this.ApiTokenKey))[this.ApiTokenKey];
        return token != undefined;
    }

    public async getUserEmail() : Promise<string | undefined> {
        return (await chrome.storage.local.get(this.UserEmailKey))[this.UserEmailKey];
    }

    public deleteUserState() {
        chrome.runtime.sendMessage({action: "fa_userLoggedOut"})
    }

    public async getDomainBlockList() : Promise<string[]> {
        return this.domainBlockList;
    }

    public async getTrackAllPages() : Promise<boolean> {
        const stored = (await chrome.storage.sync.get(this.FilterSendKey))[this.FilterSendKey];
        if (stored !== undefined) {
            return stored;
        }
        return Promise.resolve(true);
    }

}


export class SharedStateWriters extends SharedStateReaders {

    public constructor() {
        super();
        if (!(self instanceof (self as any).ServiceWorkerGlobalScope)) {
            throw "Writer exception - you can't create this object in this context.";
        }
    }

    /** Setting a new api token assumes a user log in. Good time to ping for subscription status. */
    public setApiToken(newToken : string) {
        chrome.storage.local.set({
            [this.ApiTokenKey]: newToken
        });
    }

    public setUserEmail(newEmail : string) {
        chrome.storage.local.set({
            [this.UserEmailKey]: newEmail
        })
    }
    
    /// Block a domain, add to local store, and return the number of blocked domains.
    /// Runs on backend only.
    public async addDomainBlock(domainToBlock : string) : Promise<number> {
        // call server to drop a setting by key/value
        // get local set and remove element
        // return value from server as a number
        return 0;
    }

    public setFilterSend(newVal : boolean) {
        chrome.storage.sync.set({[this.FilterSendKey]: newVal});
    }
}


