import { DomShape, UploadedDom } from "./interfaces";
import { sendDomPayload, getAQuiz } from "./webInterface";

type UploadState = 'notstarted' | 'inprogress' | 'completed' | 'error';

class ApplicationState {

    private t = "fa0_FE4lwLEoJ89lVnHQfVMHfNqYia_-nl5qizo";
    
    private domainBlockList = [
        'microsoft-my.sharepoint.com',
        'microsoft.sharepoint.com',
        'localhost',
        'statics.teams.cdn.office.net',
        'google.com',
        'bing.com'
    ];

    private filterSend = true; // only send filtered article content if true.

    private uploadRecord : (UploadedDom | null) = null;

    private uploadState : UploadState = 'notstarted';

    public uploadPage(response : DomShape) {
        if (this.uploadState != 'notstarted' && this.uploadState != 'error') {
            return;
        }

        const p = sendDomPayload(this.t, response);
        const c = p?.then( x=> {this.uploadRecord = x; return x});
    }

    public async getQuiz() {
        if (this.uploadRecord == null) {
            return undefined;
        }
    
        const quiz = getAQuiz(this.t, this.uploadRecord);
        return quiz;
    }

    public shouldOperateOnPage(host : string) : boolean {

        if (host in this.domainBlockList){
            return false;
        }
    
        if (this.filterSend && !this.isArticle()) {
            return false;
        }

        return true;
    }

    private isArticle() : boolean {
        return document.querySelector('article') !== null;
    }

}

// treat this as a singleton.
export const state = new ApplicationState();
