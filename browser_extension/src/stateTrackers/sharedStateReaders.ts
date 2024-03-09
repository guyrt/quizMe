import { domain } from "../globalSettings";
import { BasicError, LooseSetting } from "../interfaces";

export class SharedStateReaders {

    protected ApiTokenKey : string = "secret.apikey";
    protected UserEmailKey : string = "secret.email";
    protected DomainBlockListKey : string = "settings.DomainBlockList";

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

    public async getDomainBlockList(forceLoad : boolean = false) : Promise<LooseSetting[] | BasicError> {
        if (!forceLoad) {
            const domains = (await chrome.storage.local.get(this.DomainBlockListKey))[this.DomainBlockListKey];
            if ('domains' in domains) {
                return domains['domains'];
            }
        }

        return new Promise((resolve, reject) => chrome.runtime.sendMessage({action: "fa_loadBlockedDomains"}, 
            function(response : {payload: LooseSetting[]} | {error: string}) {
                if ('payload' in response) {
                    resolve(response.payload);
                } else {
                    reject("error getting domains");
                }
            })
        );
    }

    public async getTrackAllPages() : Promise<boolean> {
        const key = "settings.filtersend";
        const stored = (await chrome.storage.sync.get(key))[key];
        if (stored !== undefined) {
            return stored;
        }
        return true;
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

}


