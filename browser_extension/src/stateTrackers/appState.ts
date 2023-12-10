import { UploadedDom } from "../interfaces";
import { getAQuiz } from "../webInterface";
import { sharedState } from "./sharedState";


class ApplicationState {

    public uploadRecord : (UploadedDom | null) = null;

    public isArticle : boolean | undefined;

    public async getQuiz() {
        if (!this.isArticle) {
            return;
        }

        if (this.uploadRecord == null) {
            console.log("Waiting on an upload record");
            return;
        }
    
        const quiz = getAQuiz(await sharedState.getApiToken(), this.uploadRecord);
        return quiz;
    }

}

// treat this as a singleton.
export const state = new ApplicationState();
