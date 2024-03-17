import { BasicError } from "../../../interfaces";
import { TokenManagementWebInterface } from "../webInterface";
import fetch from 'jest-fetch-mock';

describe("webInterface.TokenManagementWebInterface.loginUser", () => {

    it("posts and returns json", async () => {
        
        const responseValue = {user: 'testuser', key: 'key'};
        fetch.mockResponseOnce(JSON.stringify(responseValue));

        var response = await (new TokenManagementWebInterface()).loginUser('username', 'password');
        expect(response).toHaveProperty('user', 'testuser');
        expect(global.fetch).toHaveBeenCalled();
    })

    it("posts and handles 401", async () => {
        
        fetch.mockResponseOnce('', {status: 401});
        try {
            var response = await (new TokenManagementWebInterface()).loginUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error.error).toHaveProperty('error', 'unauthorized');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    afterEach(() => {
        jest.clearAllMocks();
    })

})