// todo:
//  - save/retrieve loader from session history
//  - get from server.

import { QuizHistory } from "../../interfaces";
import { getQuizHistory } from "../../webInterface";

class QuizHistoryState {

    private lastReadTime : EpochTimeStamp = 0;

    private quizHistory? : QuizHistory; 

    /**
     * Get quiz results. This will get and save results locally.
     */
    public async updateLatestQuizHistory() : Promise<QuizHistory | undefined> {
        const newResults = await getQuizHistory();
        this.quizHistory = newResults;
        chrome.storage.session.set({["quizHistory"]: newResults}, () => {});
        chrome.runtime.sendMessage({action: "fa_newQuizHistory", payload: newResults});
        return this.quizHistory;
    }

    // This will either return the latest quiz history or kick off a request to the server.
    // If null is returned, then we trust the async updateLatestQuizHistory to eventually get an updated message
    // sent to interested parties.
    public async getLatestQuizHistory() : Promise<QuizHistory | undefined> {
        if (this.quizHistory != undefined) {
            return this.quizHistory;
        }

        const storedHistory = await chrome.storage.session.get("quizHistory") as QuizHistory | undefined;
        if (storedHistory != undefined) {
            this.quizHistory = storedHistory;
        } else {
            console.log("getting latest quiz history")
            this.updateLatestQuizHistory(); // async but do not wait on it.
        }
        return storedHistory;
    }

}

export const quizHistoryState = new QuizHistoryState();
