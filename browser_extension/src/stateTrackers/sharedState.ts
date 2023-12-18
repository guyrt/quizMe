

/// Track state that is shared by both front and
/// back end. They live in different contexts, so 
/// you cannot assume that they have the same 
/// state at any given time. 
/// Everything here should be stored into storage
/// when written (usually by options) and should
/// be updated via message passing.
class SharedState {

    private t = "fa0_MBWOmORGwgl2zJO2lxuoQtixZF-Q6l1u6OcARBqfBQuxfyU";

    private domainBlockList = [
        'microsoft-my.sharepoint.com',
        'microsoft.sharepoint.com',
        'localhost',
        'statics.teams.cdn.office.net',
        'google.com',
        'bing.com'
    ];

    private filterSend = true; // only send filtered article content if true.

    public async getApiToken() : Promise<string> {
        return Promise.resolve(this.t);
    }

    public async getDomainBlockList() : Promise<string[]> {
        return Promise.resolve(this.domainBlockList);
    }

    public async getFilterSend() : Promise<boolean> {
        return Promise.resolve(this.filterSend);
    }

}

export const sharedState = new SharedState();
