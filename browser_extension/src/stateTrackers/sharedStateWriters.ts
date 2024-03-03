import { LooseSetting } from "../interfaces";
import { BlockedDomainsWebInterface } from "../webInterface";
import { SharedStateReaders } from "./sharedStateReaders";


export class SharedStateWriters extends SharedStateReaders {

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
}
