import { DomShape, UploadedDom } from "./interfaces";
import { sendDomPayload, getAQuiz } from "./webInterface";

class ApplicationState {

    private t = "fa0_FE4lwLEoJ89lVnHQfVMHfNqYia_-nl5qizo";
    
    private domainBlockList = [
        'microsoft-my.sharepoint.com',
        'microsoft.sharepoint.com',
        'localhost',
        'statics.teams.cdn.office.net'
    ];

    private filterSend = true; // only send filtered article content if true.

    private uploadRecord : (UploadedDom | null) = null;

    private uploadPromise : Promise<UploadedDom> | undefined;

    public uploadPage(response : DomShape) {
        if (this.uploadPromise != undefined) {
            return;
        }

        const p = sendDomPayload(this.t, response);
        this.uploadPromise = p?.then( x=> this.uploadRecord = x);
    }

    public getQuiz() {
        this.uploadPromise?.then(() => {
            if (this.uploadRecord == null) {
                return;
            }
            const quiz = getAQuiz(this.t, this.uploadRecord);
            
        });
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


export const state = new ApplicationState();
