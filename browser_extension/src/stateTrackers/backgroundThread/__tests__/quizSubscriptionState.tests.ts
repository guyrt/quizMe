import { quizHistoryState } from "../quizSubscriptionState";

describe('QuizHistoryState.deletePageDetails', () =>{
    it('deleted page details from store', done => {
        quizHistoryState.deleteAllQuizState();

        expect(chrome.storage.local.remove).toHaveBeenCalledWith('quizHistory');
        done();
    });
});
