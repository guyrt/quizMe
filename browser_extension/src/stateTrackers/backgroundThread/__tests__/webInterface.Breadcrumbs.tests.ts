import { BasicError, BreadcrumbResponse } from "../../../interfaces";
import { BackgroundSharedStateWriter } from "../backgroundSharedStateWriter";
import { BreadcrumbsWebInterface } from "../webInterface";
import fetch from 'jest-fetch-mock';


describe("webInterface.BreadcrumbsWebInterface.getBreadcrumbsPolling", () => {

    beforeEach(() => {
        jest.clearAllMocks();

        BackgroundSharedStateWriter.prototype.getApiToken = jest.fn().mockResolvedValue("faketoken");
    });
    
    it ("posts and returns json on 200", async () => {
        fetch.mockResponseOnce(JSON.stringify([{'breadcrumbs': 'yes'}]));

        const obj = new BreadcrumbsWebInterface();

        var response : BreadcrumbResponse | BasicError = await obj.getBreadcrumbsPolling("pageId");
        expect(response).not.toHaveProperty('error');
        expect((response as BreadcrumbResponse)[0]).toHaveProperty('breadcrumbs', 'yes');
    })

    it ("returns with error on a fatal error", async () => {
        fetch.mockResponseOnce("no", {status: 500});

        try {
            var response = await (new BreadcrumbsWebInterface()).getBreadcrumbsPolling("pageId");
            fail("expected reject");
        } catch (error) {
            expect(error).toHaveProperty("error", "unknown");
        }
    })

    it ("polls on a wait error.", async () => {
        fetch.mockResponseOnce("no", {status: 202});
        fetch.mockResponseOnce(JSON.stringify([{'breadcrumbs': 'yes'}]));

        const obj = new BreadcrumbsWebInterface(0); // the zero causes no sleeps.

        var response : BreadcrumbResponse | BasicError = await obj.getBreadcrumbsPolling("pageId");
        expect(response).not.toHaveProperty('error');
        expect((response as BreadcrumbResponse)[0]).toHaveProperty('breadcrumbs', 'yes');

    })

    it ("polls on a wait error and fails after 6", async () => {
        for (var i = 0; i < 6; i++) {
            fetch.mockResponseOnce("", {status: 202});
        }
        fetch.mockResponseOnce(JSON.stringify([{'breadcrumbs': 'yes'}])); // this won't be called!

        try {
            var response = await (new BreadcrumbsWebInterface(0)).getBreadcrumbsPolling("pageId");
            fail("expected reject");
        } catch (error) {
            expect(error).toHaveProperty("error", "waitfatal");
        }

    })

    afterEach(() => {
        jest.clearAllMocks();
    })
});