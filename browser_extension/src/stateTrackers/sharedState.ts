

/// Track state that is shared by both front and
/// back end. They live in different contexts, so 
/// you cannot assume that they have the same 
/// state at any given time. 
/// Everything here should be stored into storage
/// when written (usually by options) and should
/// be updated via message passing.
class SharedState {

    private domainBlockList = [
        'microsoft-my.sharepoint.com',
        'microsoft.sharepoint.com',
        'localhost',
        'statics.teams.cdn.office.net',
        'google.com',
        'bing.com',
        'ms.portal.azure.com'
    ];

    public async getApiToken() : Promise<string | undefined> {
        return (await chrome.storage.local.get("secret.apikey"))["secret.apikey"];
    }

    public setApiToken(newToken : string) {
        chrome.storage.local.set({
            "secret.apikey": newToken
        });
    }

    public deleteApiToken() {
        chrome.storage.local.remove("secret.apikey");
    }

    public async getDomainBlockList() : Promise<string[]> {
        return Promise.resolve(this.domainBlockList);
    }

    public async getTrackAllPages() : Promise<boolean> {
        const stored = (await chrome.storage.sync.get("settings.filtersend"))['settings.filtersend'];
        if (stored !== undefined) {
            return stored;
        }
        return Promise.resolve(true);
    }

    public setFilterSend(newVal : boolean) {
        chrome.storage.sync.set({"settings.filtersend": newVal});
    }

}

export const sharedState = new SharedState();
