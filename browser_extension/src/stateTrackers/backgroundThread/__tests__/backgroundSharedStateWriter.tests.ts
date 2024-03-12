import { UserTokenResponse } from "../../../interfaces";
import { BackgroundSharedStateWriter } from "../backgroundSharedStateWriter";
import { backgroundState } from "../pageDetailsHandler";
import { QuizHistoryState } from "../quizSubscriptionState";
import { TokenManagementWebInterface } from "../webInterface";
jest.mock('../webInterface');

describe('BackgroundSharedStateWriter.logUserIn', () => {

    it('should save auth when successful login', async () => {
        const tokenResponse = {
            user: 'test@user.com',
            key: 'testkey'
        };

        TokenManagementWebInterface.prototype.loginUser = jest.fn().mockResolvedValue(tokenResponse)
        QuizHistoryState.prototype.getLatestQuizHistory = jest.fn();
        backgroundState.handleTabUpload = jest.fn();

        const backgroundSharedStateWriter = new BackgroundSharedStateWriter();
        backgroundSharedStateWriter.loadDomainBlockList = jest.fn().mockResolvedValue(null);
        
        const authInfo = await backgroundSharedStateWriter.logUserIn({username: 'un', password: 'safe'});
        expect(authInfo).toHaveProperty('user');
        expect((authInfo as UserTokenResponse).user).toBe('test@user.com')
        
        expect(authInfo).toHaveProperty('key');
        expect((authInfo as UserTokenResponse).key).toBe('hidden');

        // expect call reset
        expect(backgroundSharedStateWriter.loadDomainBlockList).toHaveBeenCalled();
        expect(QuizHistoryState.prototype.getLatestQuizHistory).toHaveBeenCalled();
        expect(backgroundState.handleTabUpload).toHaveBeenCalled();

        expect(chrome.storage.local.set).toHaveBeenCalledTimes(2);
    });

    it('should save auth when successful login', async () => {
        const tokenResponse = {
            error: 'unauthorized'
        };

        TokenManagementWebInterface.prototype.loginUser = jest.fn().mockResolvedValue(tokenResponse)
        QuizHistoryState.prototype.getLatestQuizHistory = jest.fn();
        backgroundState.handleTabUpload = jest.fn();

        const backgroundSharedStateWriter = new BackgroundSharedStateWriter();
        backgroundSharedStateWriter.loadDomainBlockList = jest.fn().mockResolvedValue(null);

        const authInfo = await backgroundSharedStateWriter.logUserIn({username: 'un', password: 'safe'});
        expect(authInfo).toHaveProperty('error');

        expect(backgroundSharedStateWriter.loadDomainBlockList).not.toHaveBeenCalled();
        expect(QuizHistoryState.prototype.getLatestQuizHistory).not.toHaveBeenCalled();
        expect(backgroundState.handleTabUpload).not.toHaveBeenCalled();

        expect(chrome.storage.local.set).not.toHaveBeenCalled();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
    });
});

describe('BackgroundSharedStateWriter.signUpUser', () => {

    it('should save auth when successful sign up', async () => {
        const tokenResponse = {
            user: 'test@user.com',
            key: 'testkey'
        };

        TokenManagementWebInterface.prototype.signUpUser = jest.fn().mockResolvedValue(tokenResponse)
        QuizHistoryState.prototype.getLatestQuizHistory = jest.fn();
        backgroundState.handleTabUpload = jest.fn();

        const backgroundSharedStateWriter = new BackgroundSharedStateWriter();
        backgroundSharedStateWriter.loadDomainBlockList = jest.fn().mockResolvedValue(null);
        const authInfo = await backgroundSharedStateWriter.signupUser({username: 'un', password: 'safe'});
        expect(authInfo).toHaveProperty('user');
        expect((authInfo as UserTokenResponse).user).toBe('test@user.com')

        expect(authInfo).toHaveProperty('key');
        expect((authInfo as UserTokenResponse).key).toBe('hidden');
        
        expect(backgroundSharedStateWriter.loadDomainBlockList).toHaveBeenCalled();
        expect(QuizHistoryState.prototype.getLatestQuizHistory).toHaveBeenCalled();
        expect(backgroundState.handleTabUpload).toHaveBeenCalled();
        
        expect(chrome.storage.local.set).toHaveBeenCalledTimes(2);
    });

    it('should not save auth when failed login', async () => {
        const tokenResponse = {
            error: 'unauthorized'
        };

        TokenManagementWebInterface.prototype.signUpUser = jest.fn().mockResolvedValue(tokenResponse)
        QuizHistoryState.prototype.getLatestQuizHistory = jest.fn();
        backgroundState.handleTabUpload = jest.fn();

        const backgroundSharedStateWriter = new BackgroundSharedStateWriter();
        backgroundSharedStateWriter.loadDomainBlockList = jest.fn().mockResolvedValue(null);

        const authInfo = await backgroundSharedStateWriter.signupUser({username: 'un', password: 'safe'});
        expect(authInfo).toHaveProperty('error');

        expect(backgroundSharedStateWriter.loadDomainBlockList).not.toHaveBeenCalled();
        expect(backgroundState.handleTabUpload).not.toHaveBeenCalled();

        expect(chrome.storage.local.set).not.toHaveBeenCalled();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });
});
