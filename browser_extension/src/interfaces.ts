export type DomClassification = {
    classification : "article" | "serp" | "unknown",
    reason : "hasArticleTag" | "dashCount" | "textContent" | "id" | "class" | "serp" | "fallthrough",
    
    // these are specific lookups that are likely candidates.
    idLookup? : string,
    classLookup? : string
}


export type DomShape = {
    dom : string,
    url : Location,
    recordTime : number,
    title : string,
    byline : string,
    readerContent : string,
    domClassification : DomClassification
    siteName : string,
    publishedTime : string
}


export interface UploadableDomShape extends DomShape {
    guid : string,
    capture_index: number
}


type QuizContext = {
    previous_quiz : Quiz
    latest_results? : number[]
}


export type VisitHistory = {
    recent_page_visits: {
        number_visits: number,
        latest_visit?: {
            id: string,
            date_added: string // datetime
        }
    },
    recent_domain_visits: {
        guid: string,
        date_added: string,
        url: string,
        host: string,
        recent_title : string
    }[]
}


export type UploadedDom = {
    raw_doc : string,
    url_obj : string,
    quiz_context? : QuizContext
    visit_history : VisitHistory
}

export type FilledQuiz = {
    owner : string,
    content : QuizQuestion[],
    id : string,
    reasoning : string,
    status : "notstarted" | "building" | "completed" | "error"
}

export type Quiz = FilledQuiz | {
    status: "error" | "building"
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

export type ChromeMessageType = 
    // these three events are a 2-directional update.
      "fa_pageLoaded" 
    | "fa_pageReloaded"  // fired if the page is a reload.
    | "fa_getCurrentPage" 
    | "fa_makequiz"
    | "fa_uploadQuizResult" 
    | "fa_noAPIToken"
    // these pair of events are a 2-direction update.
    | "fa_getQuizHistory"  // sent from SidePanel to Background and expects most recent cached history.
    | "fa_newQuizHistory"  // send from the Background when a new history is retrieved. Sidepanel should listen for it.
    | "fa_onReminderClick"  // this fires when article reminder fires on webpage.
    | "fa_onLoginReminderClick"  // fires when user clicks logged out reminder.
    | "fa_userLoggedOut"

export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}

export type QuizResponseMessage = {
    action : "fa_uploadQuizResult"
    payload : QuizResponse
}

export type QuizHistory = {
    total_quizzes : number
    quiz_allowance : number
    recent_quizzes : QuizContext[]
}

export type SinglePageDetailsChangeMessage = {
    action : "fa_activeSinglePageDetailsChange"
    payload : SinglePageDetails | {'error': string}
}


type UploadState = 'notstarted' | 'inprogress' | 'completed' | 'error' | 'donotprocess';


/// store information about a single uploaded article.
export type SinglePageDetails = {
    guid : string,
    capture_index: number,
    domClassification : DomClassification
    url : Location
    uploadState : UploadState
    uploadedDom? : UploadedDom,
    key : number,
    title : string,
}