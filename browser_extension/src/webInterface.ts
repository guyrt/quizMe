import { DomShape, Quiz, UploadedDom, QuizResponse } from "./interfaces";
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
export async function getAQuiz(payload : UploadedDom, forceReload : boolean) : Promise<Quiz | undefined> {
    const url = `${domain}/api/quiz/makequiz`;
    const apiToken = await sharedState.getApiToken() ?? "todo";
    const fullPayload = {...payload, force_recreate: forceReload};

    return callFetch(apiToken, url, fullPayload).then((q : any) => {
        if (q) {
//            if (q != undefined) {
                // todo only if it's a valid quiz.            this.quizzes[key] = quiz;
                // needs a then.
  //          }

            return q as Quiz;
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
        if (response.status == 200) {
            return response.json();
        }
        return undefined;
    })
    .catch(error => {
        console.error('Error calling API: ', error);
    });

    return p
}
