/// State object for the background
import { v4 as uuidv4 } from 'uuid';

import { BasicError, DomShape, LooseSetting, MaybeSinglePageDetails, PrivacyLevels, Quiz, SinglePageDetails, UploadableDomShape, UploadedDom, isBasicError } from "../../interfaces";
import { log } from "../../utils/logger";
import { QuizWebInterface, sendDomPayload, sendDomPayloadUpdate } from "./webInterface";
import { BackgroundSharedStateWriter } from "./backgroundSharedStateWriter";

import { PageDetailsStore } from "./pageDetailsStore";
import { QuizHistoryState } from "./quizSubscriptionState";
import { SharedStateReaders } from '../sharedStateReaders';


// todo: move quiz stuff.
class PageDetailsHandler {
    
    private quizzes : {[key: number]: Quiz} = {}

    private uploadPromises : {[key: number]: Promise<UploadedDom | BasicError>} = {}

    public async handleTabUpload(loadedUrl : string) {
        if (loadedUrl == "unknown") {
            chrome.tabs.query({currentWindow: true, active: true}, (tabs) => {
                this.handleTabs(tabs, true);
            });
        } else {
            chrome.tabs.query({currentWindow: true, url: loadedUrl}, tabs => {
                this.handleTabs(tabs, true);
            });
        }
    }

    public async handleFAAccessDOMMessage(tabId : number, response : DomShape, firstUpload : boolean) {
        console.log(`Background received dom. TabId: ${tabId}, isFirst: ${firstUpload} response:`, response);
        if (firstUpload) {
            await this.uploadPage(tabId, response);
        } else {
            await this.uploadNewVersionSamePage(tabId, response);
        }
    }

    public async uploadPage(tabId : number, domSummary : DomShape) {
        console.log("Upload started on ", tabId);
        const record = await this.getOrCreatePageDetails(tabId, domSummary);
        
        // Assume that any errors here are fatal. Some errors like cache miss are cleaned up before this.
        if (isBasicError(record)) {
            return;
        }

        if (record.uploadState == 'completed') {
            // put record back - triggers an update
            PageDetailsStore.getInstance().setPageDetails(record.key, record, true);
        }
        
        // from here, we assume record is a SimplePageRecord.
        if (!await this.shouldOperateOnPage(record)) {
            console.log(`Upload abandoned ${tabId} url ${domSummary.url.href}`);
            PageDetailsStore.getInstance().setPageDetails(record.key, {...record, uploadState: 'donotprocess'}, true);
            return;
        }
        
        if (record.uploadState != 'notstarted' && record.uploadState != 'error') {
            console.log("upload abandoned for state", record.uploadState);
            return;
        }

        const token = await this.getToken();
        if (token == undefined) {
            this.setPageUnauthorized(record.key);
            return;
        }

        const uploadableDom = this.buildUploadableDom(domSummary, record.guid, record.capture_index);
        this.uploadPromises[record.key] = sendDomPayload(token, uploadableDom);
        PageDetailsStore.getInstance().setPageDetails(record.key, {...record, uploadState: 'inprogress'}, true);

        this.uploadPromises[record.key].then((x) => {
            console.log(`Upload complete for tab ${tabId} url ${domSummary.url.href}`);
            if (isBasicError(x)) {
                Promise.reject(x);
                return;
            }

            PageDetailsStore.getInstance().setPageDetails(record.key, {...record, uploadState: 'completed', uploadedDom: x}, true);
            
            // if the page is an article then we need up to date quiz info.
            if (record.domClassification.classification == "article") {
                console.log("Bumping quiz info");
                (new QuizHistoryState()).updateLatestQuizHistory();
            }
        })
        .catch((e : BasicError) => {
            console.log("Upload had issue ", e);
            if (isBasicError(e) && e.error == "unauthorized") {
                this.setPageUnauthorized(record.key);
            } else {
                // error of known type.
                PageDetailsStore.getInstance().setPageDetails(record.key, {...record, uploadState: 'error'}, true);
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
            return this.quizzes[key];
        }

        const record = await PageDetailsStore.getInstance().getPageDetails(key);

        if (isBasicError(record)) {
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

    private setPageUnauthorized(tabId : number) {
        PageDetailsStore.getInstance().setPageDetails(tabId, {error: 'auth'});
        chrome.tabs.sendMessage(tabId, {action: "fa_noAPIToken", payload: {tabId: tabId}});
    }

    // Get token. If it's blank fire.
    private async getToken() : Promise<string | undefined> {
        return await new BackgroundSharedStateWriter().getApiToken();
    }

    private buildUploadableDom(domSummary : DomShape, guid : string, captureIndex : number) : UploadableDomShape {
        return {...domSummary, guid: guid, capture_index: captureIndex}
    }

    private updatePayloadAndReturnQuiz(record : SinglePageDetails | undefined, uploadedDom : UploadedDom | undefined) : (Quiz) {
        if (record != undefined && uploadedDom != undefined) {
            // update the dom to include the quiz.
            PageDetailsStore.getInstance().setPageDetails(record.key, {...record, uploadedDom: uploadedDom}, true);
        }

        return uploadedDom?.quiz_context || {status: "building"};
    }

    // This is used to set an empty quiz.
    private setQuiz(record : SinglePageDetails | undefined, newQuiz : Quiz) : Quiz {
        if (record?.uploadedDom != undefined) {
            PageDetailsStore.getInstance().setPageDetails(record.key, {
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

        const privacySetting : PrivacyLevels = await new BackgroundSharedStateWriter().getKVPSetting(SharedStateReaders.PrivacyLevelKey);

        if (privacySetting == 'manual') {
            return false;
        }

    

        if (privacySetting == "allArticles" || privacySetting == "allPages") {
            if (await this.blockedPage(response)){
                return false;
            } else {
                return true
            }
        }

        // assume it's allow list based.
        if (await this.allowedPage(response)) {
            return response.domClassification.classification == "article";
        }
        return false;
    }

    private async blockedPage(response : SinglePageDetails) : Promise<boolean> {
        const domainBlockList = await new BackgroundSharedStateWriter().getDomainList(false, true);

        return domainBlockList != undefined && !isBasicError(domainBlockList) && domainBlockList?.some(x => response.url.host.endsWith(x.value))
    }

    private async allowedPage(response : SinglePageDetails) : Promise<boolean> {
        // todo! you need a getDomainAllowList, or reuse the fxn.
        const domainBlockList = await new BackgroundSharedStateWriter().getDomainList(false, false);

        return domainBlockList != undefined && !isBasicError(domainBlockList) && domainBlockList?.some(x => response.url.host.endsWith(x.value))
    }

    private async getPageDetails(key : number) : Promise<SinglePageDetails> {
        let pageDetail = await PageDetailsStore.getInstance().getPageDetails(key);
        if (isBasicError(pageDetail) && pageDetail.error == 'cachemiss') {
            throw `Key not found: ${key}`;
        }
        return pageDetail as SinglePageDetails;
    }

    private async getOrCreatePageDetails(key : number, response : DomShape) : Promise<MaybeSinglePageDetails> {
        let pageDetail = await PageDetailsStore.getInstance().getPageDetails(key);
        // if (isBasicError(pageDetail) && pageDetail.error != 'auth') {
        //     return pageDetail;
        // }

        const wasError = isBasicError(pageDetail);
        const urlMismatch = wasError || (pageDetail as SinglePageDetails).url.href != response.url.href;

        if (urlMismatch) {
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
            PageDetailsStore.getInstance().setPageDetails(key, pageDetail);

            if (key in this.quizzes) {
                delete this.quizzes[key];
            }
        }

        return pageDetail;
    }

    private createCaptureIndex(recordTime : number) {
        return recordTime - 17071529563; // subtract out from start of project.
    }


    private async handleTabs(tabs : chrome.tabs.Tab[], firstUpload : boolean) {
        if (tabs[0] === undefined) {
            return;
        }
        
        //check whether user is logged in
        const token = await this.getToken();
        const tId = argMax<any, any>(tabs, 'lastAccessed').id;

        if (token == undefined) {
            this.setPageUnauthorized(tId);
            return;
        }
        
        // if yes, grant access 
        chrome.tabs.sendMessage(
            tId,
            {action: "fa_accessDOM", payload: {tabId: tId}},
            async (x) => await this.handleFAAccessDOMMessage(tId, x, firstUpload)
        );
    }
    


}

export const backgroundState = new PageDetailsHandler();



function argMax<T extends Record<K, number>, K extends keyof any>(listOfObjects: T[], key: K): T {
    const argMaxObject = listOfObjects.reduce((maxObj, currentObj) => {
      return currentObj[key] > maxObj[key] ? currentObj : maxObj;
    }, listOfObjects[0]);
    return argMaxObject;
  }