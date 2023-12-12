/// State object for the background
import { DomShape, Quiz, UploadedDom } from "../interfaces";
import { getAQuiz, sendDomPayload } from "../webInterface";
import { sharedState } from "./sharedState";

type UploadState = 'notstarted' | 'inprogress' | 'completed' | 'error';


/// store information about a single uploaded article.
/// long term likely needs to be in storage.
type SinglePageDetails = {
    clientIsArticle : boolean
    url : Location
    uploadState : UploadState
    uploadedDom? : UploadedDom,
    key : number
}

type PageDetailsMap = {
    [key: number]: SinglePageDetails
}

class BackgroundState {
    
    private pageDetails : PageDetailsMap = {}

    private quizzes : {[key: number]: Quiz} = {}

    private uploadPromises : {[key: number]: Promise<UploadedDom>} = {}

    public async uploadPage(tabId : number, response : DomShape) {

        if (!await this.shouldOperateOnPage(response)) {
            return;
        }

        const record = this.getOrCreatePageDetails(tabId, response);
        
        if (record.uploadState != 'notstarted' && record.uploadState != 'error') {
            return;
        }

        const t = await sharedState.getApiToken();

        this.uploadPromises[record.key] = sendDomPayload(t, response);
        record.uploadState = 'inprogress';

        this.uploadPromises[record.key].then((x) => {
            record.uploadState = 'completed';
            record.uploadedDom = x;
        })
        .catch(() => {
            record.uploadState = 'error';
        });
    }

    public async getOrCreateAQuiz(key : number) : Promise<Quiz | undefined> {
        if (key in this.quizzes) {
            return Promise.resolve(this.quizzes[key]);
        }

        if (!(key in this.pageDetails)) {
            return Promise.resolve(undefined);
        }

        const record = this.pageDetails[key];
        
        if (!record.clientIsArticle) {
            return Promise.resolve(undefined);
        }

        if (record.uploadState == 'inprogress' || record.uploadedDom == null) {
            console.log("Waiting on an upload record");
            return Promise.resolve(undefined);
        }
    
        const quiz = getAQuiz(await sharedState.getApiToken(), record.uploadedDom);
        if (quiz != undefined) {
// todo only if it's a valid quiz.            this.quizzes[key] = quiz;
// needs a then.
        }
        return quiz;
    }

    private async shouldOperateOnPage(response : DomShape) : Promise<boolean> {

        if (response.url.host in await sharedState.getDomainBlockList()){
            return false;
        }
    
        if (!response.clientIsArticle) {
            return false;
        }

        return true;
    }

    private getOrCreatePageDetails(key : number, response : DomShape) : SinglePageDetails {
        if (!(key in this.pageDetails) || (this.pageDetails[key].url.href != response.url.href)) {
            // If this is a new page OR this is a change of site in same tab.
            console.log(`Writing new page ${response.url.href} for tab ${key}`);
            this.pageDetails[key] = {
                clientIsArticle: response.clientIsArticle,
                uploadState: 'notstarted',
                url: response.url,
                key: key
            }
        }

        return this.pageDetails[key];
    }

}

export const backgroundState = new BackgroundState();
