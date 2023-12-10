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
    key : string
}

type PageDetailsMap = {
    [key: string]: SinglePageDetails
}

class BackgroundState {
    
    private pageDetails : PageDetailsMap = {}

    private quizzes : {[key: string]: Quiz} = {}

    private uploadPromises : {[key: string]: Promise<UploadedDom>} = {}

    public async uploadPage(response : DomShape) {

        if (!await this.shouldOperateOnPage(response)) {
            return;
        }

        const record = this.getOrCreatePageDetails(response);
        
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

    public async getOrCreateAQuiz(key : string) : Promise<Quiz | undefined> {
        if (key in this.quizzes) {
            return this.quizzes[key];
        }

        if (!(key in this.pageDetails)) {
            return;
        }

        const record = this.pageDetails[key];
        
        if (!record.clientIsArticle) {
            return;
        }

        if (record.uploadState == 'inprogress' || record.uploadedDom == null) {
            console.log("Waiting on an upload record");
            return;
        }
    
        const quiz = await getAQuiz(await sharedState.getApiToken(), record.uploadedDom);
        this.quizzes[key] = quiz;
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

    private getOrCreatePageDetails(response : DomShape) : SinglePageDetails {
        const key = response.url.href;
        if (!(key in this.pageDetails)) {
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
