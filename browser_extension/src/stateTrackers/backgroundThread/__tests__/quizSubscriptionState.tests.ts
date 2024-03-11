import { QuizHistory } from "../../../interfaces";
import { quizHistoryState } from "../quizSubscriptionState";

describe('QuizHistoryState.deletePageDetails', () =>{
    it('deleted page details from store', done => {
        quizHistoryState.deleteAllQuizState();

        expect(chrome.storage.local.remove).toHaveBeenCalledWith('quizHistory');
        done();
    });
});

const mockUpdateLatestQuizHistory = jest.fn();
quizHistoryState.updateLatestQuizHistory = mockUpdateLatestQuizHistory;

describe('QuizHistoryState.getLatestQuizHistory', () => {
    beforeEach(() => {
        // Clear all instances and calls to constructor and all methods:
        mockUpdateLatestQuizHistory.mockClear();
        (chrome.storage.session.get as jest.Mock).mockClear();
    });

    it('should call updateLatestQuizHistory when quizHistory is undefined', async () => {
        (chrome.storage.session.get as jest.Mock).mockImplementation(() => Promise.resolve({}));
        await quizHistoryState.getLatestQuizHistory();
        expect(mockUpdateLatestQuizHistory).toHaveBeenCalled();
    });

    it('should call updateLatestQuizHistory even when quizHistory is available', async () => {
        const mockQuizHistory : QuizHistory = {
            total_quizzes : 10,
            quiz_allowance : 14,
            recent_quizzes : [],
            num_days_month : 2,
            streak : 2
        };

        (chrome.storage.session.get as jest.Mock).mockImplementation(() => Promise.resolve({ quizHistory: mockQuizHistory }));
        const result = await quizHistoryState.getLatestQuizHistory();
        expect(result).toEqual(mockQuizHistory);
        expect(mockUpdateLatestQuizHistory).toHaveBeenCalled();
    });
});