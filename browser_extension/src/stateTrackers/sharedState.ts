

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
        'outlook.office.com', // safety check from outlook.
        'microsoft.sharepoint.com',
        'localhost',
        'totalrewards.azurefd.net',
        'statics.teams.cdn.office.net',
        'microsoft-my.sharepoint-df.com',
        'ms.portal.azure.com',
        'sapsf.com',
        'login.microsoftonline.com' // logins
    ];

    public async getApiToken() : Promise<string | undefined> {
        return (await chrome.storage.local.get("secret.apikey"))["secret.apikey"];
    }

    /** Setting a new api token assumes a user log in. Good time to ping for subscription status. */
    public setApiToken(newToken : string) {
        chrome.storage.local.set({
            "secret.apikey": newToken
        });
    }

    public setUserEmail(newEmail : string) {
        chrome.storage.local.set({
            "secret.email": newEmail
        })
    }

    public async getUserEmail() : Promise<string | undefined> {
        return (await chrome.storage.local.get("secret.email"))["secret.email"];
    }

    public deleteUserState() {
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
