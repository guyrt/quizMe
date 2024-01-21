import { ChromeMessage, QuizHistory } from "../../interfaces";

class QuizHistoryBroker {
    private quizHistory : QuizHistory | undefined = undefined;

    private listeners: ((state: QuizHistory) => void)[] = [];

    public subscribe(listener: (state: QuizHistory) => void): void {
        this.listeners.push(listener);
    }

    public unsubscribe(listener: (state: QuizHistory) => void): void {
        this.listeners = this.listeners.filter(l => l !== listener);
    }
    
    public setQuizHistory(payload: QuizHistory) {
        this.quizHistory = payload;
        this.publish();
    }

    public getQuizzesRemaining() {
        if ((this.quizHistory?.quiz_allowance ?? 101) > 100) {
            return Infinity;
        }
        return Math.max(0, ((this.quizHistory?.quiz_allowance ?? Infinity) - (this.quizHistory?.recent_quizzes.length ?? 0)));
    }

    public trigger() {
        chrome.runtime.sendMessage({ action: "fa_getQuizHistory", payload: {} }, (_quizHistory: QuizHistory | undefined) => {
            console.log("Received quiz history: ", _quizHistory);
            if (_quizHistory != undefined) {
                this.setQuizHistory(_quizHistory);
            }
        });
    }

    private publish() {
        this.listeners.forEach(listener => {
            if (this.quizHistory != undefined) {
                listener(this.quizHistory);
            }
        });
    }
}

export const quizHistoryBroker = new QuizHistoryBroker();


chrome.runtime.onMessage.addListener((message : ChromeMessage, sender) => {
    if (message.action == "fa_newQuizHistory") {
        const qh : QuizHistory | undefined = message.payload;
        if (qh != undefined) {
            quizHistoryBroker.setQuizHistory(qh);
        }
    }
    return true;
});