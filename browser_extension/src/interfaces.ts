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
    owner : string,
    content : QuizQuestion[],
    id : string,
    reasoning : string
}

export type QuizQuestion = {
    question : string,
    answers : QuizAnswer[]
}

export type QuizAnswer = {
    answer : string,
    correct? : number
}

export type ChromeMessageType = "fa_pageLoaded" | "fa_makequiz"


export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}
