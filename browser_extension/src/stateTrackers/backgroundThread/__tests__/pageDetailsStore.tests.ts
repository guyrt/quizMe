import { PageDetailsStore } from "../pageDetailsStore";

describe('PageDetailsStore.deletePageDetails', () =>{
    it('deleted page details from store', done => {
        PageDetailsStore.getInstance().deletePageDetails(123);

        expect(chrome.storage.local.remove).toHaveBeenCalledWith('singlepagedetails.123');
        done();
    });
})