export type DomShape = {
    dom : string,
    url : Location,
    recordTime : number,
    title : string,

    clientIsArticle : boolean
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


export type ChromeMessageType = "fa_pageLoaded" | "fa_makequiz"


export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}
