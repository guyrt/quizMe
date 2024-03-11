// todo:
//  - save/retrieve loader from session history
//  - get from server.

import { BasicError, QuizHistory, QuizResponse } from "../../interfaces";
import { QuizWebInterface } from "./webInterface";

export class QuizHistoryState {

    /**
     * Get quiz results. This will get and save results locally.
     */
    public async updateLatestQuizHistory() : Promise<QuizHistory | BasicError> {
        const webInterface = new QuizWebInterface();
        const newResults = await webInterface.getQuizHistory();
        console.log("received new quiz history: ", newResults);
        if (!('error' in newResults)) {
            chrome.storage.session.set({["quizHistory"]: newResults});
        }
        return newResults;
    }

    // This will either return the latest quiz history or kick off a request to the server.
    // If null is returned, then we trust the async updateLatestQuizHistory to eventually get an updated message
    // sent to interested parties.
    public async getLatestQuizHistory() : Promise<QuizHistory | BasicError> {
        
        const storedHistory = (await chrome.storage.session.get("quizHistory"))['quizHistory'] as QuizHistory | undefined;
        if (storedHistory == undefined) {
            return this.updateLatestQuizHistory();
        }
        this.updateLatestQuizHistory(); // update in background so we're up to date in case other things loaded. we could gate.
        return storedHistory;
    }

    public async uploadQuizResult(payload : QuizResponse) : Promise<QuizHistory | BasicError> {
        const webInterface = new QuizWebInterface();
        const history = await webInterface.uploadQuizResults(payload);
        if (!('error' in history)) {
            chrome.storage.session.set({["quizHistory"]: history});
        }
        return history;
    }

    public async deleteAllQuizState() {
        chrome.storage.local.remove('quizHistory');
    }

}
