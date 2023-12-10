/// State object for the background
import { DomShape, UploadedDom } from "../interfaces";
import { sendDomPayload } from "../webInterface";
import { sharedState } from "./sharedState";

type UploadState = 'notstarted' | 'inprogress' | 'completed' | 'error';


class BackgroundState {
    
    private uploadState : UploadState = 'notstarted';

    private isArticle : boolean | undefined;

    private domUploadPromise : Promise<UploadedDom> | undefined;

    public async uploadPage(response : DomShape) {
        if (this.uploadState != 'notstarted' && this.uploadState != 'error') {
            return;
        }

        const t = await sharedState.getApiToken();
        this.domUploadPromise = sendDomPayload(t, response);
        this.uploadState = 'inprogress';
        this.domUploadPromise.then((x) => {
            this.uploadState = 'completed';

            chrome.runtime.sendMessage({
                'action': 'domupload',
                'requestId': response.requestId,
                'payload': {
                    'uploadeddom': x,
                    'isarticle': this.getIsArticle()
                }
            });
        })
        .catch(() => {
            this.uploadState = 'error';
        });
    }

    public async shouldOperateOnPage(host : string) : Promise<boolean> {

        if (host in await sharedState.getDomainBlockList()){
            return false;
        }
    
        if (await sharedState.getDomainBlockList() && !this.getIsArticle()) {
            return false;
        }

        return true;
    }

    private getIsArticle() : boolean {
        if (this.isArticle !== undefined) {
            return this.isArticle;
        }
        this.isArticle = document.querySelector('article') !== null;
        return this.isArticle;
    }
}

export const backgroundState = new BackgroundState();
