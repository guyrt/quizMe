/// State object for the background
import { v4 as uuidv4 } from 'uuid';

import { BasicError, DomShape, MaybeSinglePageDetails, Quiz, SinglePageDetails, UploadableDomShape, UploadedDom } from "../../interfaces";
import { log } from "../../utils/logger";
import { QuizWebInterface, sendDomPayload, sendDomPayloadUpdate } from "./webInterface";
import { BackgroundSharedStateWriter } from "./backgroundSharedStateWriter";

import { pageDetailsStore } from "./pageDetailsStore";
import { QuizHistoryState } from "./quizSubscriptionState";


// todo: move quiz stuff.
class PageDetailsHandler {
    
    private quizzes : {[key: number]: Quiz} = {}

    private uploadPromises : {[key: number]: Promise<UploadedDom>} = {}

    public async uploadPage(tabId : number, domSummary : DomShape) {
        console.log("Upload started on ", tabId);
        const record = await this.getOrCreatePageDetails(tabId, domSummary);
        
        // Assume that any errors here are fatal. Some errors like cache miss are cleaned up before this.
        if ('error' in record) {
            pageDetailsStore.setPageDetails(tabId, record);
            return;
        }

        // from here, we assume record is a SimplePageRecord.
        if (!await this.shouldOperateOnPage(record)) {
            console.log(`Upload abandoned ${tabId} url ${domSummary.url.href}`);
            pageDetailsStore.setPageDetails(record.key, {...record, uploadState: 'donotprocess'}, true);
            return;
        }
        
        if (record.uploadState != 'notstarted' && record.uploadState != 'error') {
            console.log("upload abandoned for state", record.uploadState);
            return;
        }

        const token = await this.getToken();
        if (token == undefined) {
            pageDetailsStore.setPageDetails(record.key, {error: 'auth'});
            return;
        }

        const uploadableDom = this.buildUploadableDom(domSummary, record.guid, record.capture_index);
        this.uploadPromises[record.key] = sendDomPayload(token, uploadableDom);
        pageDetailsStore.setPageDetails(record.key, {...record, uploadState: 'inprogress'}, true);

        this.uploadPromises[record.key].then((x) => {
            console.log(`Upload complete for tab ${tabId} url ${domSummary.url.href}`);
            pageDetailsStore.setPageDetails(record.key, {...record, uploadState: 'completed', uploadedDom: x}, true);
            
            // if the page is an article then we need up to date quiz info.
            if (record.domClassification.classification == "article") {
                console.log("Bumping quiz info");
                (new QuizHistoryState()).updateLatestQuizHistory();
            }
        })
        .catch((e : BasicError) => {
            console.log("Upload had issue ", e);
            if ('error' in e) {
                pageDetailsStore.setPageDetails(record.key, {error: 'auth'});
            } else {
                // error of known type.
                pageDetailsStore.setPageDetails(record.key, {...record, uploadState: 'error'}, true);
            }
        });
    }

    /**
     * Handle upload of a new version of the same page. 
     * Current upload may be in progress. If so we need to wait for it, get the id, then use it to send the update.
     * 
     * @param tabId 
     * @param response 
     */
    public async uploadNewVersionSamePage(tabId : number, domSummary : DomShape) {
        console.log(`Uploading new version of ${tabId}`);
        const token = await this.getToken();
        if (token == undefined) {return;}

        let record : SinglePageDetails;
        try {
            record = await this.getPageDetails(tabId)
            record.capture_index = this.createCaptureIndex(domSummary.recordTime);
        } catch (e) {
            console.error(e);
            return;
        }

        // this doesn't set loading/unloading and I'm not sure if we should.
        this.uploadPromises[tabId].then(() => {
            const uploadableDom = this.buildUploadableDom(domSummary, record.guid, record.capture_index);
            this.uploadPromises[record.key] = sendDomPayloadUpdate(token, uploadableDom);
        });
    }

    public async getOrCreateAQuiz(key : number, forceReload : boolean) : Promise<Quiz> {
        const quizwebInterface = new QuizWebInterface();
        if (!forceReload && key in this.quizzes) {
            log(`Outputting cached quiz for key ${key}`);
            return Promise.resolve(this.quizzes[key]);
        }

        const record = await pageDetailsStore.getPageDetails(key);

        if ('error' in record) {
            log(`Key ${key} not in page details. Returning no quiz.`)
            return Promise.resolve({'status': 'error'});
        }
        
        if (record.domClassification.classification != "article") {
            log(`Key ${key} is not an article. Returning no quiz.`);
            return Promise.resolve(this.setQuiz(record, {'status': 'error'}));
        }

        if (record.uploadState == 'inprogress' || record.uploadedDom == null) {
            console.log("Waiting on an upload record");
            if (key in this.uploadPromises) {
                const upstream = this.uploadPromises[key];
                return upstream.then(async () => {
                    if (record.uploadedDom) {
                        const uploadedDom = await quizwebInterface.getAQuiz(record.uploadedDom, forceReload);

                        return this.updatePayloadAndReturnQuiz(record, uploadedDom);
                    }
                    return this.setQuiz(record, {'status': 'building'});
                });
            } else {
                return this.setQuiz(record, {'status': 'error'});
            }
        }
    
        quizwebInterface.getAQuiz(record.uploadedDom, forceReload).then(newDom => this.updatePayloadAndReturnQuiz(record, newDom));
        return this.setQuiz(record, {'status': 'building'});
    }

    private async getToken() : Promise<string | undefined> {
        return await new BackgroundSharedStateWriter().getApiToken();
    }

    private buildUploadableDom(domSummary : DomShape, guid : string, captureIndex : number) : UploadableDomShape {
        return {...domSummary, guid: guid, capture_index: captureIndex}
    }

    private updatePayloadAndReturnQuiz(record : SinglePageDetails | undefined, uploadedDom : UploadedDom | undefined) : (Quiz) {
        if (record != undefined && uploadedDom != undefined) {
            // update the dom to include the quiz.
            pageDetailsStore.setPageDetails(record.key, {...record, uploadedDom: uploadedDom}, true);
        }

        return uploadedDom?.quiz_context || {status: "building"};
    }

    // This is used to set an empty quiz.
    private setQuiz(record : SinglePageDetails | undefined, newQuiz : Quiz) : Quiz {
        if (record?.uploadedDom != undefined) {
            pageDetailsStore.setPageDetails(record.key, {
                ...record, 
                uploadedDom: {
                    ...record.uploadedDom,
                    quiz_context: newQuiz
                }
            }, true);
        }
        return newQuiz;
    }

    private async shouldOperateOnPage(response : SinglePageDetails) : Promise<boolean> {

        const domainBlockList = await new BackgroundSharedStateWriter().getDomainBlockList();
        if (domainBlockList != undefined && !('error' in domainBlockList) && domainBlockList?.some(x => response.url.host.endsWith(x.value))){
            return false;
        }
    
        if (await new BackgroundSharedStateWriter().getTrackAllPages() == true) {
            return true;
        }

        if (response.domClassification.classification != "article") {
            return false;
        }

        return true;
    }

    private async getPageDetails(key : number) : Promise<SinglePageDetails> {
        let pageDetail = await pageDetailsStore.getPageDetails(key);
        if ('error' in pageDetail && pageDetail.error == 'cachemiss') {
            throw `Key not found: ${key}`;
        }
        return pageDetail as SinglePageDetails;
    }

    private async getOrCreatePageDetails(key : number, response : DomShape) : Promise<MaybeSinglePageDetails> {
        let pageDetail = await pageDetailsStore.getPageDetails(key);
        if ('error' in pageDetail && pageDetail.error == 'auth') {
            return pageDetail;
        }

        const missingKey = 'error' in pageDetail && pageDetail.error == 'cachemiss';
        const urlMismatch = missingKey || (pageDetail as SinglePageDetails).url.href != response.url.href;

        if (missingKey || urlMismatch) {
            // If this is a new page OR this is a change of site in same tab.
            pageDetail =  {
                guid: uuidv4(),
                capture_index: this.createCaptureIndex(response.recordTime),
                domClassification: response.domClassification,
                uploadState: 'notstarted',
                url: response.url,
                key: key,
                uploadedDom: undefined,
                title: response.title
            };
            pageDetailsStore.setPageDetails(key, pageDetail);

            if (key in this.quizzes) {
                delete this.quizzes[key];
            }
        }

        return Promise.resolve(pageDetail);
    }

    private createCaptureIndex(recordTime : number) {
        return recordTime - 17071529563; // subtract out from start of project.
    }

}

export const backgroundState = new PageDetailsHandler();
