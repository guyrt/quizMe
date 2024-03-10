import { BasicError, LooseSetting } from "../../interfaces";
import { pageDetailsStore } from "./pageDetailsStore";
import { BlockedDomainsWebInterface, TokenManagementWebInterface } from "./webInterface";
import { SharedStateReaders } from "../sharedStateReaders";

/** Note: poor name. This actually is the background processor version with elevated capabilitites. */
export class BackgroundSharedStateWriter extends SharedStateReaders {

    constructor() {
        super();
        if (!(self instanceof (self as any).ServiceWorkerGlobalScope)) {
            throw "Writer exception - you can't create this object in this context.";
        }
    }
    
    /// Block a domain, add to local store, and return the number of blocked domains.
    /// Runs on backend only.
    public async addDomainBlock(domainToBlock : string) : Promise<boolean> {
        // call server to drop a setting by key/value
        const webSetResponse = new BlockedDomainsWebInterface().addBlockedDomain(domainToBlock);
        // get local set and remove element
        // return value from server as a number
        return webSetResponse;
    }

    public async dropDomainBlock(domainToUnblock : string) : Promise<number> {
        const webDelete = new BlockedDomainsWebInterface().deleteBlockedDomain(domainToUnblock);
        return webDelete;
    }

    public setFilterSend(newVal : boolean) {
        chrome.storage.sync.set({["settings.filtersend"]: newVal});
    }

    public async loadDomainBlockList() : Promise<LooseSetting[]> {
        try {
            const domains = await new BlockedDomainsWebInterface().getBlockedDomains();
            chrome.storage.local.set({[this.DomainBlockListKey]: {domains: domains}});
            return domains;
        } catch {
            // save an error.
            chrome.storage.local.set({[this.DomainBlockListKey]: {error: "domain fetch"}});
        }

        return [];
    }

    public async getDomainBlockList(forceLoad : boolean = false) : Promise<LooseSetting[] | BasicError> {
        if (!forceLoad) {
            const domains = (await chrome.storage.local.get(this.DomainBlockListKey))[this.DomainBlockListKey];
            if ('domains' in domains) {
                return domains['domains'];
            }
        }

        return this.loadDomainBlockList();
    }

    public async logUserOut() {
        (new TokenManagementWebInterface()).logUserOut();
        this.deleteUserState();
    }
    
    public async getApiToken() : Promise<string | undefined> {
        const token = (await chrome.storage.local.get(this.ApiTokenKey))[this.ApiTokenKey];

        if (token == undefined) {
            // if a token doesn't exist, nuke local state.
            this.deleteUserState();
        }
        return token;
    }

    private deleteUserState() {
        // nuke storage
        pageDetailsStore.deleteAllPageDetails();
    }
}
