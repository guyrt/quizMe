import { BasicError, LooseSetting } from "../interfaces";

export class SharedStateReaders {

    protected static ApiTokenKey : string = "secret.apikey";
    protected static UserEmailKey : string = "secret.email";
    protected static DomainBlockListKey : string = "settings.DomainBlockList";
    protected static DomainAllowListKey : string = "settings.DomainAllowList";

    public async hasApiToken() {
        const token = (await chrome.storage.local.get(SharedStateReaders.ApiTokenKey))[SharedStateReaders.ApiTokenKey];
        return token != undefined;
    }

    public async getUserEmail() : Promise<string | undefined> {
        return (await chrome.storage.local.get(SharedStateReaders.UserEmailKey))[SharedStateReaders.UserEmailKey];
    }

    public async getDomainList(forceLoad : boolean = false, getBlock : boolean = true) : Promise<LooseSetting[] | BasicError> {
        const key = getBlock ? SharedStateReaders.DomainBlockListKey : SharedStateReaders.DomainAllowListKey;
        const loadDomainsEvent = getBlock ? "fa_loadBlockedDomains" : "fa_loadAllowedDomains";
        
        if (!forceLoad) {
            const domains = (await chrome.storage.local.get(key))[SharedStateReaders.DomainBlockListKey];
            if ('domains' in domains) {
                return domains['domains'];
            }
        }

        return new Promise((resolve, reject) => chrome.runtime.sendMessage({action: loadDomainsEvent}, 
            function(response : {payload: LooseSetting[]} | {error: string}) {
                if ('payload' in response) {
                    resolve(response.payload);
                } else {
                    reject("error getting domains");
                }
            })
        );
    }

}


