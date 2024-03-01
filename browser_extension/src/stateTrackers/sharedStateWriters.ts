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
    public async addDomainBlock(domainToBlock : string) : Promise<number> {
        // call server to drop a setting by key/value
        // get local set and remove element
        // return value from server as a number
        const webDelete = new BlockedDomainsWebInterface().deleteBlockedDomain(domainToBlock);

        return webDelete;
    }

    public setFilterSend(newVal : boolean) {
        chrome.storage.sync.set({["settings.filtersend"]: newVal});
    }

    public async loadDomainBlockList() : Promise<string[]> {
        const domains = await new BlockedDomainsWebInterface().getBlockedDomains();
        return domains;
    }
}
