import { QuizHistory } from "../../../interfaces";
import { QuizHistoryState } from "../quizSubscriptionState";
import { QuizWebInterface } from "../webInterface";
jest.mock('../webInterface');


const mockQuizHistory : QuizHistory = {
    total_quizzes : 10,
    quiz_allowance : 14,
    recent_quizzes : [],
    num_days_month : 2,
    streak : 2
};

const mockError = {
    error: "testunknown"
};


describe('QuizHistoryState.updateLatestQuizHistory', () => {

    it('should save quiz history when no error', async () => {
        QuizWebInterface.prototype.getQuizHistory = jest.fn().mockResolvedValue(mockQuizHistory);
        const quizHistoryState = new QuizHistoryState();
        const result = await quizHistoryState.updateLatestQuizHistory();

        // check that we did call the session set.
        expect(chrome.storage.session.set).toHaveBeenCalled();
        expect(result).toEqual(mockQuizHistory);
    });

    it('should not save quiz history when there is an error', async () => {
        
        QuizWebInterface.prototype.getQuizHistory = jest.fn().mockResolvedValue(mockError);
        
        const quizHistoryState = new QuizHistoryState();
        const result = await quizHistoryState.updateLatestQuizHistory();
    
        expect(result).toEqual(mockError);
        expect(chrome.storage.session.set).not.toHaveBeenCalled();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });
});


describe('QuizHistoryState.deletePageDetails', () =>{
    it('deleted page details from store', done => {
        const quizHistoryState = new QuizHistoryState();
        quizHistoryState.deleteAllQuizState();

        expect(chrome.storage.local.remove).toHaveBeenCalledWith('quizHistory');
        done();
    });
});

describe('QuizHistoryState.getLatestQuizHistory', () => {

    const mockUpdateLatestQuizHistory = jest.fn();
    const quizHistoryState = new QuizHistoryState();
    quizHistoryState.updateLatestQuizHistory = mockUpdateLatestQuizHistory;

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
        (chrome.storage.session.get as jest.Mock).mockImplementation(() => Promise.resolve({ quizHistory: mockQuizHistory }));
        const result = await quizHistoryState.getLatestQuizHistory();
        expect(result).toEqual(mockQuizHistory);
        expect(mockUpdateLatestQuizHistory).toHaveBeenCalled();
    });
});


describe('QuizHistoryState.uploadQuizResult', () => {

    it('should update history when history is returned ', async () => {
        QuizWebInterface.prototype.uploadQuizResults = jest.fn().mockResolvedValue(Promise.resolve(mockQuizHistory));
        const quizHistoryState = new QuizHistoryState();

        await quizHistoryState.uploadQuizResult({quiz_id: 'id', selection: [0]});
        expect(chrome.storage.session.set).toHaveBeenCalled();
    });

    it('should not update history when error is returned', async () => {
        QuizWebInterface.prototype.uploadQuizResults = jest.fn().mockResolvedValue(Promise.resolve(mockError));
        const quizHistoryState = new QuizHistoryState();

        await quizHistoryState.uploadQuizResult({quiz_id: 'id', selection: [0]});
        expect(chrome.storage.session.set).not.toHaveBeenCalled();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });
});