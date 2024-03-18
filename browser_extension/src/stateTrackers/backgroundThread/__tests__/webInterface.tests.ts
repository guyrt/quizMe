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
            await (new TokenManagementWebInterface()).loginUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'unauthorized');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles 409", async () => {
        
        fetch.mockResponseOnce('', {status: 409});
        try {
            await (new TokenManagementWebInterface()).loginUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'usernameexists');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles othererror", async () => {
        
        fetch.mockResponseOnce('', {status: 420});
        try {
            await (new TokenManagementWebInterface()).loginUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'unknown');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles failure", async () => {
        
        fetch.mockRejectOnce(new Error("totalfailure"));
        try {
            await (new TokenManagementWebInterface()).loginUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    afterEach(() => {
        jest.clearAllMocks();
    })
})


describe("webInterface.TokenManagementWebInterface.signUpUser", () => {

    it("posts and returns json", async () => {
        
        const responseValue = {user: 'testuser', key: 'key'};
        fetch.mockResponseOnce(JSON.stringify(responseValue));

        var response = await (new TokenManagementWebInterface()).signUpUser('username', 'password');
        expect(response).toHaveProperty('user', 'testuser');
        expect(global.fetch).toHaveBeenCalled();
    })

    it("posts and handles 401", async () => {
        
        fetch.mockResponseOnce('', {status: 401});
        try {
            await (new TokenManagementWebInterface()).signUpUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'unauthorized');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles 409", async () => {
        
        fetch.mockResponseOnce('', {status: 409});
        try {
            await (new TokenManagementWebInterface()).signUpUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'usernameexists');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles othererror", async () => {
        
        fetch.mockResponseOnce('', {status: 420});
        try {
            await (new TokenManagementWebInterface()).signUpUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(error).toHaveProperty('error', 'unknown');
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    it("posts and handles failure", async () => {
        
        fetch.mockRejectOnce(new Error("totalfailure"));
        try {
            await (new TokenManagementWebInterface()).signUpUser('username', 'password');
            fail("expected reject")
        } catch (error : any) {
            expect(global.fetch).toHaveBeenCalled();
        }
    })

    afterEach(() => {
        jest.clearAllMocks();
    })
})