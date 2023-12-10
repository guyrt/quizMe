export type DomShape = {
    dom : string,
    url : Location,
    recordTime : number,
    title : string,

    requestId : string // way to track which request was used.
}

export type UploadedDom = {
    raw_doc : string,
    url_obj : string
}

export type Quiz = {
    document : string,
    quizPk : string,
    question : string
}


export type ChromeMessageType = "domupload" | "fa_pageLoaded"


export type ChromeMessage = {
    action : ChromeMessageType,
    requestId : string,
    payload : any
}
