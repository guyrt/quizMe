import { DomShape } from "./interfaces";


export function sendPayload(payload : DomShape) {
    const t = "fa0_FE4lwLEoJ89lVnHQfVMHfNqYia_-nl5qizo";
    const data = JSON.stringify(payload);

    const domainBlockList = [
        'microsoft-my.sharepoint.com'
    ];

    if (payload.url.host in domainBlockList){
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
