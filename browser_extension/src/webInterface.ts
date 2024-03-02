import { UploadedDom, UploadableDomShape, QuizResponse, Quiz, QuizHistory, LooseSetting } from "./interfaces";
import { SharedStateWriters } from "./stateTrackers/sharedStateWriters";
import { domain } from "./globalSettings";


const sharedStateWriter = new SharedStateWriters();


export async function uploadQuizResults(payload : QuizResponse) : Promise<undefined> {
    const url = `${domain}/api/quiz/uploadresults`;
    const token = await sharedStateWriter.getApiToken() ?? "todo";
    return post(token, url, payload);
}


export async function sendDomPayload(token : string, payload : UploadableDomShape) : Promise<UploadedDom> {
    console.log("sendDomPayload");
    const url = `${domain}/api/browser/writehtml`;

    return post(token, url, payload); // TODO - this could return undefined.
}

export async function sendDomPayloadUpdate(token : string, payload : UploadableDomShape) : Promise<UploadedDom> {
    console.log("sendDomPayload");
    const url = `${domain}/api/browser/rewritehtml`;

    return post(token, url, payload); // TODO - this could return undefined.
}

export class QuizWebInterface {

    public async getAQuiz(payload : UploadedDom, forceReload : boolean) : Promise<UploadedDom> {
        const url = `${domain}/api/quiz/makequiz`;
        const apiToken = await sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return {...payload, quiz_context: {previous_quiz: {status: "error"}}};
        }

        const fullPayload = {...payload, force_recreate: forceReload};

        return post(apiToken, url, fullPayload).then((q : any) => {
            // note: overwrites only quizzes. This is critical to avoid 
            // clobbering other parts of a dom payload.
            if (q) {
                return {...payload, quiz_context: (q as UploadedDom).quiz_context};
            } else {
                return {...payload, quiz_context: {previous_quiz: this.createErrorQuiz()}};
            }
        })
        .catch(error => {
            console.error('Error calling API: ', error);
            return {...payload, quiz_context: {previous_quiz: this.createErrorQuiz()}};
        });
    }


    public async getQuizHistory() : Promise<QuizHistory | undefined> {
        const url = `${domain}/api/quiz/stats`;
        const apiToken = await sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return undefined;
        }
        
        return get(apiToken, url).then(x => {
            if (x != undefined) {
                return x as QuizHistory;
            } else {
                return undefined;
            }
        }).catch(error => {
            console.error('Error calling QuizHistory: ', error);
            return undefined;
        });
    }

    private createErrorQuiz() : Quiz {
        return {
            status: "error",
            content: [],
            id: "error",
            owner: "error",
            reasoning: "error"
        };
    }

}


export class BlockedDomainsWebInterface {
    private specificKeyUrl = `${domain}/api/user/settings/domain.exclude`;

    public async addBlockedDomain(domain : string) : Promise<boolean> {
        const apiToken = await sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return false;
        }

        return post(apiToken, this.specificKeyUrl, {value: domain}).then(x => true).catch(e => false);
    }

    public async deleteBlockedDomain(domain : string) : Promise<number> {
        const apiToken = await sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return -1;
        }
        
        return await callDelete(apiToken, this.specificKeyUrl, {value: domain}).then((deletePayload : any) => {
            return deletePayload.num_objects_deleted;
        });
    }

    public async getBlockedDomains() : Promise<LooseSetting[]> {
        const apiToken = await sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return [];
        }

        return get<LooseSetting[]>(apiToken, this.specificKeyUrl);
    }
}


// Todo - eventually may need a payload... or combine with post...
function get<OutT>(token : string, url : string) : Promise<OutT>{
    const headers = {
        'X-API-KEY': token,
        'Content-Type': 'application/json'
    };

    const p = fetch(url, {
        method: "GET",
        headers: headers
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    })

    return p

}


function post<InT, OutT>(token : string, url : string, payload : InT) : Promise<OutT> {
    console.log(`Posting to ${url}`);

    const headers = {
        'X-API-KEY': token,
        'Content-Type': 'application/json'
    };

    const p = fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    })

    return p
}


function callDelete<OutT>(token : string, url : string, payload : {[key: string]: string}) : Promise<OutT> {
    const queryString = new URLSearchParams(payload).toString();

    const headers = {
        'X-API-KEY': token,
        'Content-Type': 'application/json'
    };

    const p = fetch(`${url}?${queryString}`, {
        method: "DELETE",
        headers: headers
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    })

    return p;
}
