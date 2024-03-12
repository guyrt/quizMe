import { UploadedDom, UploadableDomShape, QuizResponse, Quiz, QuizHistory, LooseSetting, BasicError, UserTokenResponse, isBasicError } from "../../interfaces";
import { BackgroundSharedStateWriter } from "./backgroundSharedStateWriter";
import { domain } from "../../globalSettings";


export async function sendDomPayload(token : string, payload : UploadableDomShape) : Promise<UploadedDom | BasicError> {
    console.log("sendDomPayload");
    const url = `${domain}/api/browser/writehtml`;

    return post(token, url, payload); // TODO - this could return undefined.
}

export async function sendDomPayloadUpdate(token : string, payload : UploadableDomShape) : Promise<UploadedDom | BasicError> {
    console.log("sendDomPayload");
    const url = `${domain}/api/browser/rewritehtml`;

    return post(token, url, payload); // TODO - this could return undefined.
}

export class QuizWebInterface {

    private sharedStateWriter : BackgroundSharedStateWriter = new BackgroundSharedStateWriter();

    public async getAQuiz(payload : UploadedDom, forceReload : boolean) : Promise<UploadedDom> {
        const url = `${domain}/api/quiz/makequiz`;
        const apiToken = await this.sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return {...payload, quiz_context: {status: "error"}};
        }

        const fullPayload = {...payload, force_recreate: forceReload};

        return post(apiToken, url, fullPayload).then((q : any) => {
            // note: overwrites only quizzes. This is critical to avoid 
            // clobbering other parts of a dom payload.
            if (q) {
                return {...payload, quiz_context: (q as UploadedDom).quiz_context};
            } else {
                return {...payload, quiz_context: this.createErrorQuiz()};
            }
        })
        .catch(error => {
            console.error('Error calling API: ', error);
            return {...payload, quiz_context: this.createErrorQuiz()};
        });
    }

    public async getQuizHistory() : Promise<QuizHistory | BasicError> {
        const url = `${domain}/api/quiz/stats`;
        const apiToken = await this.sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return {error: 'unauth'};
        }
        
        return get(apiToken, url).then(x => {
            if (x != undefined) {
                return x as QuizHistory;
            } else {
                return {error: 'unexpected response'};
            }
        }).catch(error => {
            console.error('Error calling QuizHistory: ', error);
            return {error: error};
        });
    }

    public async uploadQuizResults(payload : QuizResponse) : Promise<QuizHistory | BasicError> {
        const url = `${domain}/api/quiz/uploadresults`;
        const token = await this.sharedStateWriter.getApiToken() ?? "todo";
        return post(token, url, payload).then((payload) => {
            if (payload != undefined) {
                return payload as QuizHistory;
            } else {
                return {error : 'unexpected response'};
            }
        }).catch(e => {
            return {error: e}
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
    private settingsUrl = `${domain}/api/user/settings`;
    private settingsKey = 'domain.exclude';
    private specificKeyUrl = `${this.settingsUrl}/${this.settingsKey}`;

    private sharedStateWriter : BackgroundSharedStateWriter = new BackgroundSharedStateWriter();

    public async addBlockedDomain(domain : string) : Promise<boolean> {
        const apiToken = await this.sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return false;
        }

        return post(apiToken, this.settingsUrl, {key: this.settingsKey, value: domain}).then(x => true).catch(e => false);
    }

    public async deleteBlockedDomain(domain : string) : Promise<number> {
        const apiToken = await this.sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return -1;
        }
        
        return await callDelete(apiToken, this.specificKeyUrl, {value: domain}).then((deletePayload : any) => {
            return deletePayload.num_objects_deleted;
        });
    }

    public async getBlockedDomains() : Promise<LooseSetting[]> {
        const apiToken = await this.sharedStateWriter.getApiToken();
        if (apiToken == undefined) {
            return [];
        }

        return get<LooseSetting[]>(apiToken, this.specificKeyUrl).then(x => {
            if (isBasicError(x)) {
                return [];
            }
            return x;
        });
    }
}


export class TokenManagementWebInterface {

    private sharedStateWriter : BackgroundSharedStateWriter = new BackgroundSharedStateWriter();

    public async logUserOut() {
        // delete the token.
        const url = `${domain}/api/user/tokens/delete`;
        const token = await this.sharedStateWriter.getApiToken();
        if (token == undefined) {
            return false;
        }

        const headers = {
            'X-API-KEY': token
        }

        return fetch(url, {
            method: "DELETE",
            headers: headers
        }).then(() => true);
    }

    public async loginUser(username : string, password : string) : Promise<UserTokenResponse | BasicError> {
        const url = `${domain}/api/user/tokens/create`;

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        return this.postForm(url, formData);
    }

    public async signUpUser(username : string, password : string) : Promise<UserTokenResponse | BasicError> {
        const url = `${domain}/api/user/create`;

        const formData = new FormData();
        formData.append('email', username);
        formData.append('password', password);

        return this.postForm(url, formData);        
    }

    private postForm(url : string, formData : FormData) : Promise<UserTokenResponse | BasicError> {
        return fetch(url, {
            method: "POST",
            body: formData
        }).then(response => {
            if (response.ok) {
                return response.json();
            }
            if (response.status == 401) {
                Promise.reject({error: 'unauthorized'});
            } 
            Promise.reject({error: "unknown"});
        }).catch(e => {
            Promise.reject({error: e});
        })
    }
}


// Todo - eventually may need a payload... or combine with post...
function get<OutT>(token : string, url : string) : Promise<OutT | BasicError>{
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
        if (response.status == 401) {
            return Promise.reject({error: 'unauthorized'})
        }
        return Promise.reject({error: 'unknown'});
    })

    return p

}


function post<InT, OutT>(token : string, url : string, payload : InT) : Promise<OutT | BasicError> {
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
        if (response.status == 401) {
            return Promise.reject({error: 'unauthorized'});
        }
        return Promise.reject({error: 'unknown'});
    })

    return p
}


function callDelete<OutT>(token : string, url : string, payload : {[key: string]: string}) : Promise<OutT | BasicError> {
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
