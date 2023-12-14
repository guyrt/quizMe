/// State object for the background
import { DomShape, Quiz, UploadedDom } from "../interfaces";
import { log } from "../utils/logger";
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

    public getPageDetails(tabId : number) : SinglePageDetails | undefined {
        return this.pageDetails[tabId];
    }

    public async uploadPage(tabId : number, response : DomShape) {

        const record = this.getOrCreatePageDetails(tabId, response);

        if (!await this.shouldOperateOnPage(record)) {
            log(`Upload abandoned ${tabId} url ${response.url}`);
            return;
        }
        
        if (record.uploadState != 'notstarted' && record.uploadState != 'error') {
            return;
        }

        const t = await sharedState.getApiToken();

        this.uploadPromises[record.key] = sendDomPayload(t, response);
        record.uploadState = 'inprogress';

        this.uploadPromises[record.key].then((x) => {
            record.uploadState = 'completed';
            record.uploadedDom = x;
            log(`Upload complete for tab ${tabId} url ${response.url.href}`);
        })
        .catch(() => {
            record.uploadState = 'error';
        });
    }

    public async getOrCreateAQuiz(key : number) : Promise<Quiz | undefined> {
        if (key in this.quizzes) {
            log(`Outputting cached quiz for key ${key}`);
            return Promise.resolve(this.quizzes[key]);
        }

        if (!(key in this.pageDetails)) {
            log(`Key ${key} not in page details. Returning no quiz.`)
            return Promise.resolve(undefined);
        }

        const record = this.pageDetails[key];
        
        if (!record.clientIsArticle) {
            log(`Key ${key} is not an article. Returning no quiz.`);
            return Promise.resolve(undefined);
        }

        const apiToken = await sharedState.getApiToken();

        if (record.uploadState == 'inprogress' || record.uploadedDom == null) {
            console.log("Waiting on an upload record");
            if (key in this.uploadPromises) {
                const upstream = this.uploadPromises[key];
                return upstream.then(() => {
                    if (record.uploadedDom) {
                        const quiz = getAQuiz(apiToken, record.uploadedDom);
                    }
                    return quiz;
                })
            } else {
                return Promise.resolve(undefined);
            }
        }
    
        const quiz = getAQuiz(apiToken, record.uploadedDom);
        return quiz;
    }

    private async shouldOperateOnPage(response : SinglePageDetails) : Promise<boolean> {

        if (response.url.host in await sharedState.getDomainBlockList()){
            return false;
        }
    
        if (!response.clientIsArticle) {
            return false;
        }

        return true;
    }

    private getOrCreatePageDetails(key : number, response : DomShape) : SinglePageDetails {
        const missingKey = !(key in this.pageDetails);
        missingKey && log(`tabId ${key} missing from pageDetails`);

        const urlMismatch = this.pageDetails[key]?.url?.href != response.url.href;
        urlMismatch && log(`url mismatch: stored ${this.pageDetails[key]?.url?.href} but need ${response.url.href}`);

        if (missingKey || urlMismatch) {
            // If this is a new page OR this is a change of site in same tab.
            console.log(`Writing new page ${response.url.href} for tab ${key}.`);
            console.log(`Is article: ${response.clientIsArticle}`);
            this.pageDetails[key] = {
                clientIsArticle: response.clientIsArticle,
                uploadState: 'notstarted',
                url: response.url,
                key: key,
                uploadedDom: undefined
            }
            if (key in this.quizzes) {
                delete this.quizzes[key];
            }
        }

        return this.pageDetails[key];
    }

}

export const backgroundState = new BackgroundState();
