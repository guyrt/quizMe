// todo:
//  - save/retrieve loader from session history
//  - get from server.

import { QuizHistory } from "../../interfaces";

class QuizHistoryState {

    private lastReadTime : EpochTimeStamp = 0;

    private quizHistory? : QuizHistory; 

    /**
     * Poll for quiz results. This will get and save results locally.
     */
    public async getLatestQuizHistory() : Promise<QuizHistory | undefined> {
        return;
    }

    /**
     * Get local history if it exists. Otherwise get it again.
     */
    public async getStoredQuizHistory() : Promise<any> {

    }

}

export const quizHistoryState = new QuizHistoryState();
