import { pageDetailsStore } from "../pageDetailsStore";

describe('PageDetailsStore.deletePageDetails', () =>{
    it('deleted page details from store', done => {
        pageDetailsStore.deletePageDetails(123);

        expect(chrome.storage.local.remove).toHaveBeenCalledWith('singlepagedetails.123');
        done();
    });
})