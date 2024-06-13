import { BasicError, QuizHistory, QuizResponse, isBasicError } from "../../interfaces";

class QuizHistoryBroker {
    private quizHistory : QuizHistory | undefined = undefined;

    private listeners: ((state: QuizHistory) => void)[] = [];

    public subscribe(listener: (state: QuizHistory) => void): void {
        this.listeners.push(listener);
    }

    public unsubscribe(listener: (state: QuizHistory) => void): void {
        this.listeners = this.listeners.filter(l => l !== listener);
    }
    
    public getQuizzesRemaining() {
        if ((this.quizHistory?.quiz_allowance ?? 101) > 100) {
            return Infinity;
        }
        return Math.max(0, ((this.quizHistory?.quiz_allowance ?? Infinity) - (this.quizHistory?.recent_quizzes.length ?? 0)));
    }

    public getTotalQuizzes() {
        return this.quizHistory?.total_quizzes;
    }

    public trigger() {
        chrome.runtime.sendMessage({ action: "fa_getQuizHistory", payload: {} }, (quizHistory: QuizHistory | BasicError) => {
            if (quizHistory != undefined && !isBasicError(quizHistory)) {
                this.setQuizHistory(quizHistory);
            }
        });
    }

    public uploadQuizResults(payload : QuizResponse) {
        // console.log(`In uploadQuizResutlts ${payload.quiz_id}`);
        chrome.runtime.sendMessage({action: "fa_uploadQuizResult", payload: payload}, (quizHistory: QuizHistory | BasicError) => {
            if (quizHistory != undefined && !isBasicError(quizHistory)) {
                this.setQuizHistory(quizHistory);
            }
        })
    }

    private setQuizHistory(payload: QuizHistory) {
        this.quizHistory = payload;
        this.publish();
    }
    
   
    public getQuizHistory(){
        // console.log(`Current history state ${this.quizHistory}`);
        return this.quizHistory;
    }

    //  save most recent quiz right before it's  uploaded, and mark it as scored. Only unmark it when we get a new make quiz. 
    private publish() {
        this.listeners.forEach(listener => {
            if (this.quizHistory != undefined) {
                listener(this.quizHistory);
            }
        });
    }
}

export const quizHistoryBroker = new QuizHistoryBroker();
quizHistoryBroker.trigger();  // preload.
