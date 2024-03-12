import { UserTokenResponse } from "../../../interfaces";
import { BackgroundSharedStateWriter } from "../backgroundSharedStateWriter";
import { TokenManagementWebInterface } from "../webInterface";
jest.mock('../webInterface');

describe('BackgroundSharedStateWriter.logUserIn', () => {

    it('should save auth when successful login', async () => {
        const tokenResponse = {
            user: 'test@user.com',
            key: 'testkey'
        };

        TokenManagementWebInterface.prototype.loginUser = jest.fn().mockResolvedValue(tokenResponse)

        const backgroundSharedStateWriter = new BackgroundSharedStateWriter();
        const authInfo = await backgroundSharedStateWriter.logUserIn({username: 'un', password: 'safe'});
        expect(authInfo).toHaveProperty('user');
        expect((authInfo as UserTokenResponse).user).toBe('test@user.com')

        expect(authInfo).toHaveProperty('key');
        expect((authInfo as UserTokenResponse).key).toBe('hidden');

        expect(chrome.storage.local.set).toHaveBeenCalledTimes(2);
    });
});
