export type DomClassification = {
    classification : "article" | "unknown",
    reason : "hasArticleTag" | "dashCount" | "textContent" | "id" | "class" | "fallthrough",
    
    // these are specific lookups that are likely candidates.
    idLookup? : string,
    classLookup? : string
}


export type DomShape = {
    dom : string,
    url : Location,
    recordTime : number,
    title : string,

    domClassification : DomClassification
}

export type UploadedDom = {
    raw_doc : string,
    url_obj : string,
    url_context? : {
        previous_quiz : {
            owner : string // should be a guid
            content : {
                question : string,
                answers: {
                    answer : string,
                    correct? : number
                }[]
            }[],
            id : string,
            reasoning : string
        },
        latest_results? : number[]
    }
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

export type QuizResponse = {
    quiz_id : string,
    selection : number[]
}

export type ChromeMessageType = "fa_pageLoaded" | "fa_makequiz" | "fa_checkIsArticle" | "fa_uploadQuizResult"


export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}

export type QuizResponseMessage = {
    action : "fa_uploadQuizResult"
    payload : QuizResponse
}
