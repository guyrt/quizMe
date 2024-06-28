import { DeleteDomainAllowMessage, QuizResponseMessage, SetKVPSetting } from "../interfaces";
import { BackgroundSharedStateWriter } from "../stateTrackers/backgroundThread/backgroundSharedStateWriter";
import { QuizHistoryState } from "../stateTrackers/backgroundThread/quizSubscriptionState";

export const handleQuizResponseMessage = async (message : QuizResponseMessage, sendResponse : (response : any) => void) => {
    const quizHistory = await (new QuizHistoryState()).uploadQuizResult(message.payload);
    sendResponse(quizHistory);
}


export const setKVPSetting = (message : SetKVPSetting) => {
    const key = message.payload.key;
    const value = message.payload.value;
    (new BackgroundSharedStateWriter()).setKVPSetting(key, value);
}


export const handleDeleteDomainAllow = (message : DeleteDomainAllowMessage, sendResponse : (response : any) => void) => {
    (new BackgroundSharedStateWriter()).dropDomainAllow(message.payload.domain).then(
        domains => sendResponse({payload: domains})
    ).catch(e => {
        sendResponse({error: "error getting allowed domains"});
    })
    return true;
}