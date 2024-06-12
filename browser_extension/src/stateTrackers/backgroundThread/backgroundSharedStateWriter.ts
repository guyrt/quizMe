import { BasicError, LooseSetting, UserTokenResponse, isBasicError } from "../../interfaces";
import { PageDetailsStore } from "./pageDetailsStore";
import { AllowedDomainsWebInterface, BlockedDomainsWebInterface, TokenManagementWebInterface } from "./webInterface";
import { SharedStateReaders } from "../sharedStateReaders";
import { QuizHistoryState } from "./quizSubscriptionState";
import { backgroundState } from "./pageDetailsHandler";

/** Note: poor name. This actually is the background processor version with elevated capabilitites. */
export class BackgroundSharedStateWriter extends SharedStateReaders {

    constructor() {
        super();
    }
    
    /// Block a domain, add to local store, and return the number of blocked domains.
    /// Runs on backend only.
    public async addDomainBlock(domainToBlock : string) : Promise<boolean> {
        // call server to drop a setting by key/value
        const webSetResponse = new BlockedDomainsWebInterface().addDomain(domainToBlock);
        // get local set and remove element
        // return value from server as a number
        return webSetResponse;
    }

    public async addAllowDomain(domain : string) : Promise<boolean> {
        return new AllowedDomainsWebInterface().addDomain(domain);
    }

    public async dropDomainBlock(domain : string) : Promise<number> {
        const webDelete = new BlockedDomainsWebInterface().deleteDomain(domain);
        return webDelete;
    }

    public async dropDomainAllow(domain : string) : Promise<number> {
        const webDelete = new AllowedDomainsWebInterface().deleteDomain(domain);
        return webDelete;
    }

    public setKVPSetting(key : string, val : any) {
        chrome.storage.sync.set({[key]: val});
    }

    public async getKVPSetting(key : string) {
        return await chrome.storage.sync.get(key);
    }

    public async loadDomainBlockList() : Promise<LooseSetting[]> {
        try {
            const domains = await new BlockedDomainsWebInterface().getDomains();
            chrome.storage.local.set({[SharedStateReaders.DomainBlockListKey]: {domains: domains}});
            return domains;
        } catch {
            // save an error.
            chrome.storage.local.set({[SharedStateReaders.DomainBlockListKey]: {error: "domain fetch"}});
        }

        return [];
    }

    public async loadDomainAllowList() : Promise<LooseSetting[]> {
        try {
            const domains = await new AllowedDomainsWebInterface().getDomains();
            chrome.storage.local.set({[SharedStateReaders.DomainAllowListKey]: {domains: domains}});
            return domains;
        } catch {
            // save an error.
            chrome.storage.local.set({[SharedStateReaders.DomainAllowListKey]: {error: "domain fetch"}});
        }

        return [];
    }

    public async getDomainBlockList(forceLoad : boolean = false) : Promise<LooseSetting[] | BasicError> {
        if (!forceLoad) {
            const domains = (await chrome.storage.local.get(SharedStateReaders.DomainBlockListKey))[SharedStateReaders.DomainBlockListKey];
            if ('domains' in domains) {
                return domains['domains'];
            }
        }

        return this.loadDomainBlockList();
    }

    public async logUserOut() {
        (new TokenManagementWebInterface()).logUserOut();
        await this.deleteUserState();
    }

    /** Setting a new api token assumes a user log in. Good time to ping for subscription status. */
    public setApiToken(newToken : string) {
        chrome.storage.local.set({
            [SharedStateReaders.ApiTokenKey]: newToken
        });
    }

    public setUserEmail(newEmail : string) {
        chrome.storage.local.set({
            [SharedStateReaders.UserEmailKey]: newEmail
        })
    }
    
    
    public async getApiToken() : Promise<string | undefined> {
        const token = (await chrome.storage.local.get(SharedStateReaders.ApiTokenKey))[SharedStateReaders.ApiTokenKey];

        if (token == undefined) {
            // if a token doesn't exist, nuke local state.
            await this.deleteUserState();
        }

        return token;
    }

    public async logUserIn(payload: {username: string, password: string}) : Promise<UserTokenResponse | BasicError> {
        const result = (new TokenManagementWebInterface()).loginUser(payload.username, payload.password);
        return this.handleUserSignup(result);
    }

    public async signupUser(payload: {username: string, password: string}) : Promise<UserTokenResponse | BasicError> {
        const result = (new TokenManagementWebInterface()).signUpUser(payload.username, payload.password);
        return this.handleUserSignup(result);
    }

    private handleUserSignup(result : Promise<UserTokenResponse | BasicError>) : Promise<UserTokenResponse | BasicError> {
        return result.then(async x => {
            if (isBasicError(x)) {
                return Promise.reject(x)
            } else {
                this.setApiToken(x.key);
                this.setUserEmail(x.user);

                // trigger data updates
                await (new QuizHistoryState()).getLatestQuizHistory();
                await this.loadDomainBlockList();
                await backgroundState.handleTabUpload("unknown");

                // scrub key but the rest of the payload can be sent back.
                x.key = 'hidden';
                return Promise.resolve(x);
            }
        }).catch(x => {
            return x
        });
    }

    private async deleteUserState() {
        // nuke storage
        await PageDetailsStore.getInstance().deleteAllPageDetails();
        await (new QuizHistoryState()).deleteAllQuizState();
        await chrome.storage.local.remove(SharedStateReaders.ApiTokenKey);
    }
}
