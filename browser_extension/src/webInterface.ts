import { DomShape, Quiz, UploadedDom } from "./interfaces";

const domain = "http://localhost:8000";


export function sendDomPayload(token : string, payload : DomShape) : Promise<UploadedDom> {
    const url = `${domain}/api/browser/writehtml`;

    return callFetch(token, url, payload);
}

/// Request a quiz
export async function getAQuiz(token : string, payload : UploadedDom) : Promise<Quiz> {
    const url = `${domain}/api/quiz/makequiz`;

    // The model has a JSON string that we want to parse and return.
    return callFetch(token, url, payload).then((q : any) => {
        q.content = JSON.parse(q.content);
        return q as Quiz;
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
    .then(response => response.json())
    .catch(error => {
        console.error('Error calling API: ', error);
    });

    return p
}
