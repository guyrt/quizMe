import { DomShape, UploadedDom, QuizResponse } from "./interfaces";
import { sharedState } from "./stateTrackers/sharedState";
import { domain } from "./globalSettings";

export async function uploadQuizResults(payload : QuizResponse) : Promise<undefined> {
    const url = `${domain}/api/quiz/uploadresults`;
    const token = await sharedState.getApiToken() ?? "todo";
    return callFetch(token, url, payload);
}


export function sendDomPayload(token : string, payload : DomShape) : Promise<UploadedDom> {
    const url = `${domain}/api/browser/writehtml`;

    return callFetch(token, url, payload);
}

/// Request a quiz
export async function getAQuiz(payload : UploadedDom, forceReload : boolean) : Promise<UploadedDom | undefined> {
    const url = `${domain}/api/quiz/makequiz`;
    const apiToken = await sharedState.getApiToken() ?? "todo";
    const fullPayload = {...payload, force_recreate: forceReload};

    return callFetch(apiToken, url, fullPayload).then((q : any) => {
        if (q) {
            return q as UploadedDom;
        } else {
            return undefined;
        }
    });
}


function callFetch<InT, OutT>(token : string, url : string, payload : InT, method = "POST") : Promise<OutT> {
    const headers = {
        'X-API-KEY': token,
        'Content-Type': 'application/json'
    };

    const p = fetch(url, {
        method: method,
        headers: headers,
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else if (response.status == 401) {
            // unauthorized - fire generic signal.
            chrome.runtime.sendMessage({action: "fa_noAPIToken"});
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    })
    .catch(error => {
        console.error('Error calling API: ', error);
    });

    return p
}
