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
    quiz_context? : {
        previous_quiz : Quiz
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

export type ChromeMessageType = "fa_pageLoaded" | "fa_makequiz" | "fa_checkIsArticle" | "fa_uploadQuizResult" | "fa_noAPIToken"


export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}

export type QuizResponseMessage = {
    action : "fa_uploadQuizResult"
    payload : QuizResponse
}

export type SinglePageDetailsChangeMessage = {
    action : "fa_activeSinglePageDetailsChange"
    payload : SinglePageDetails
}


type UploadState = 'notstarted' | 'inprogress' | 'completed' | 'error' | 'donotprocess';


/// store information about a single uploaded article.
/// long term likely needs to be in storage.
export type SinglePageDetails = {
    domClassification : DomClassification
    url : Location
    uploadState : UploadState
    uploadedDom? : UploadedDom,
    key : number
}