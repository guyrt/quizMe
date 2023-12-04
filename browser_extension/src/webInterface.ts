import { DomShape } from "./interfaces";


export function sendPayload(payload : DomShape) {
    const t = "fa0_FE4lwLEoJ89lVnHQfVMHfNqYia_-nl5qizo";
    const data = JSON.stringify(payload);

    const domainBlockList = [
        'microsoft-my.sharepoint.com',
        'microsoft.sharepoint.com',
        'localhost',
        'statics.teams.cdn.office.net'
    ];

    const filterSend = true; // only send filtered article content if true.

    if (payload.url.host in domainBlockList){
        return;
    }

    if (filterSend && !isArticle()) {
        return;
    }

    const url = "http://localhost:8000/api/browser/writehtml";
    const headers = {
        'X-API-KEY': t,
        'Content-Type': 'application/json'
    };

    fetch(url, {
        method: "POST",
        headers: headers,
        body: data
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error calling API: ', error);
    });
}


function isArticle() : boolean {
    return document.querySelector('article') !== null;
}