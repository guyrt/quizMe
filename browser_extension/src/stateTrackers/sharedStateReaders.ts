import { BasicError, LooseSetting } from "../interfaces";

export class SharedStateReaders {

    protected static ApiTokenKey : string = "secret.apikey";
    protected static UserEmailKey : string = "secret.email";
    protected static DomainBlockListKey : string = "settings.DomainBlockList";

    public async hasApiToken() {
        const token = (await chrome.storage.local.get(SharedStateReaders.ApiTokenKey))[SharedStateReaders.ApiTokenKey];
        return token != undefined;
    }

    public async getUserEmail() : Promise<string | undefined> {
        return (await chrome.storage.local.get(SharedStateReaders.UserEmailKey))[SharedStateReaders.UserEmailKey];
    }

    public async getDomainBlockList(forceLoad : boolean = false) : Promise<LooseSetting[] | BasicError> {
        if (!forceLoad) {
            const domains = (await chrome.storage.local.get(SharedStateReaders.DomainBlockListKey))[SharedStateReaders.DomainBlockListKey];
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

}


