export type DomShape = {
    dom : string,
    url : Location,
    recordTime : number,
    title : string
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
    type : ChromeMessageType,
    payload : any
}
