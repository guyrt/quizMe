/// State object for the background
import { DomShape, Quiz, UploadedDom } from "../interfaces";
import { log } from "../utils/logger";
import { getAQuiz, sendDomPayload } from "../webInterface";
import { sharedState } from "./sharedState";

import { pageDetailsStore, SinglePageDetails } from "./pageDetailsStore";


class BackgroundState {
    
    private quizzes : {[key: number]: Quiz} = {}

    private uploadPromises : {[key: number]: Promise<UploadedDom>} = {}

    public async uploadPage(tabId : number, response : DomShape) {

        const record = await this.getOrCreatePageDetails(tabId, response);

        if (!await this.shouldOperateOnPage(record)) {
            log(`Upload abandoned ${tabId} url ${response.url}`);
            return;
        }
        
        if (record.uploadState != 'notstarted' && record.uploadState != 'error') {
            return;
        }

        const t = await sharedState.getApiToken() ?? "todo";

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

    public async getOrCreateAQuiz(key : number, forceReload : boolean) : Promise<Quiz | undefined> {
        if (!forceReload && key in this.quizzes) {
            log(`Outputting cached quiz for key ${key}`);
            return Promise.resolve(this.quizzes[key]);
        }

        const record = await pageDetailsStore.getPageDetails(key);

        if (record == undefined) {
            log(`Key ${key} not in page details. Returning no quiz.`)
            return Promise.resolve(undefined);
        }
        
        if (record.domClassification.classification != "article") {
            log(`Key ${key} is not an article. Returning no quiz.`);
            return Promise.resolve(undefined);
        }

        if (record.uploadState == 'inprogress' || record.uploadedDom == null) {
            console.log("Waiting on an upload record");
            if (key in this.uploadPromises) {
                const upstream = this.uploadPromises[key];
                return upstream.then(async () => {
                    if (record.uploadedDom) {
                        const quiz = await getAQuiz(record.uploadedDom, forceReload);
                        return quiz;
                    }
                    return undefined;
                });
            } else {
                return Promise.resolve(undefined);
            }
        }
    
        const quiz = getAQuiz(record.uploadedDom, forceReload);
        return quiz;
    }

    private async shouldOperateOnPage(response : SinglePageDetails) : Promise<boolean> {

        if (response.url.host in await sharedState.getDomainBlockList()){
            return false;
        }
    
        if (await sharedState.getFilterSend() == false) {
            // If filtering is turned off and it's not in the block list, then send.
            return true;
        }

        if (response.domClassification.classification != "article") {
            return false;
        }

        return true;
    }

    private async getOrCreatePageDetails(key : number, response : DomShape) : Promise<SinglePageDetails> {
        let pageDetail = await pageDetailsStore.getPageDetails(key);
        const missingKey = pageDetail == undefined;
        missingKey && log(`tabId ${key} missing from pageDetails`);

        const urlMismatch = pageDetail?.url?.href != response.url.href;
        urlMismatch && log(`url mismatch: stored ${pageDetail?.url?.href} but need ${response.url.href}`);

        if (missingKey || urlMismatch) {
            // If this is a new page OR this is a change of site in same tab.
            console.log(`Writing new page ${response.url.href} for tab ${key}.`);
            console.log(`Is article: ${response.domClassification}`);
            pageDetail =  {
                domClassification: response.domClassification,
                uploadState: 'notstarted',
                url: response.url,
                key: key,
                uploadedDom: undefined
            };
            pageDetailsStore.setPageDetails(key, pageDetail);

            if (key in this.quizzes) {
                delete this.quizzes[key];
            }
        }

        return pageDetail as SinglePageDetails;
    }

}

export const backgroundState = new BackgroundState();
