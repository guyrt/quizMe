export type DomClassification = {
    classification : "article" | "serp" | "unknown",
    reason : "hasArticleTag" | "dashCount" | "textContent" | "id" | "class" | "serp" | "fallthrough" | "randomForest" | "metaTag" | "propertyAttribute"|"urlContent",

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


export type RecentDomainVisits = {
    title: string,
    head: string,
    urls: {
        guid: string,
        date_added: string,
        url: string,
        host: string,
        recent_title : string
    }[]
}


export type VisitHistory = {
    recent_page_visits: {
        number_visits: number,
        latest_visit?: {
            id: string,
            date_added: string // datetime
        }
    },
    recent_domain_visits: RecentDomainVisits[]
}


export type UploadedDom = {
    raw_doc : string,
    url_obj : string,
    quiz_context? : Quiz
    visit_history : VisitHistory
}

export type FilledQuiz = {
    owner : string,
    content : QuizQuestion[],
    id : string,
    reasoning : string,
    status : "notstarted" | "building" | "completed" | "error",
    quiz_results : number[] | undefined
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
    | "fa_activeSinglePageDetailsChange" // fired when a page's contents have changed.
    | "fa_getCurrentPage"
    | "fa_makequiz"
    | "fa_uploadQuizResult"

    // unauth
    | "fa_noAPIToken"  // fired from backend to the browser tab.
    | "fa_sidePanelNoAPIToken"  // fired from backend to the side panel.

    // these pair of events are a 2-direction update.
    | "fa_getQuizHistory"  // sent from SidePanel to Background and expects most recent cached history.
    | "fa_onReminderClick"  // this fires when article reminder fires on webpage.
    
    | "fa_onLoginReminderClick"  // fires when user clicks logged out reminder.
    | "fa_addNewDomainBlock"  // message from sidepanel adding a new domain to block.
    | "fa_addNewDomainAllow" // message from sidepanel to add a new domain to allow.
    | "fa_loadBlockedDomains" // message from sidepanel to backend to load blocked domains.
    | "fa_loadAllowedDomains" // message from sidepanel to backend to load allowed domains.
    | "fa_deleteDomainBlock"
    | "fa_deleteDomainAllow"  // message from sidepanel to remove an allowed domain.
    | "fa_setKVPSetting" // message for sending new settings values.
    | "fa_logUserOut" // message from options surfaces to backend to nuke api token.
    | "fa_signUserIn" // message from options surfaces to backend to try to sign a user in.
    | "fa_createNewUser" // message from options surfaces to backend to try to create a new user.
    | "fa_getbreadcrumbs" // message from sidepanel to backend to retrieve breadcrumbs

export type ChromeMessage = {
    action : ChromeMessageType,
    payload : any
}

export type SignUserInMessage = {
    action: "fa_signUserIn"
    payload: {
        username: string,
        password: string
    }
}
export const isSignUserInMessage = (o: ChromeMessage): o is SignUserInMessage => o.action === "fa_signUserIn"

export type SetKVPSetting = {
    action: "fa_setKVPSetting"
    payload: {
        key: string
        value: any
    }
}
export const isSetKVPSetting = (o: ChromeMessage): o is SetKVPSetting => o.action === "fa_setKVPSetting";

export type QuizResponseMessage = {
    action : "fa_uploadQuizResult"
    payload : QuizResponse
}
export const isQuizResponseMessage = (o: ChromeMessage): o is QuizResponseMessage => o.action == "fa_uploadQuizResult";

export type GetCurrentPageMessage = {
    action : "fa_getCurrentPage"
    payload : undefined
}
export const isGetCurrentPageMessage = (o : ChromeMessage): o is GetCurrentPageMessage => o.action === "fa_getCurrentPage";

export type PageLoadedMessage = {
    action: "fa_pageLoaded"
    payload: {
        url: string
    }
}
export const isPageLoadedMessage = (o : ChromeMessage): o is PageLoadedMessage => o.action === "fa_pageLoaded";

export type PageReloadedMessage = {
    action: "fa_pageReloaded"
    payload: {
        tabId: number
    }
}
export const isPageReloadedMessage = (o : ChromeMessage): o is PageReloadedMessage => o.action === "fa_pageReloaded";

export type GetBreadcrumbsMessage = {
    action: "fa_getbreadcrumbs"
    payload: {
        pageId: string
    }
}
export const isGetBreadcrumbsMessage = (o : ChromeMessage): o is GetBreadcrumbsMessage => o.action === "fa_getbreadcrumbs";

export type DeleteDomainAllowMessage = {
    action: "fa_deleteDomainAllow"
    payload: {
        domain : string
    }
}
export const isDeleteDomainAllowMessage = (o : ChromeMessage): o is DeleteDomainAllowMessage => o.action === "fa_deleteDomainAllow";


export type AddNewDomainAllow = {
    action: "fa_addNewDomainAllow"
    payload: {
        domain: "<unknown>" | string
    }
}
export const isAddNewDomainAllow = (o: ChromeMessage): o is AddNewDomainAllow => o.action === "fa_addNewDomainAllow";

export type SinglePageDetailsChangeMessage = {
    action : "fa_activeSinglePageDetailsChange"
    payload : SinglePageDetails | BasicError
}
export const isSinglePageDetailsChangeMessage = (o: ChromeMessage): o is SinglePageDetailsChangeMessage => o.action === "fa_activeSinglePageDetailsChange";



export type QuizHistory = {
    total_quizzes : number
    quiz_allowance : number
    recent_quizzes : Quiz[],
    num_days_month : number,
    streak : number,
    stripe_redirect : string  // URL to redirect
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

export type SinglePageDetailsErrorState =  {
    error: 'auth' |   // issue with auth - generally fatal.
           'nopage' |  // no page shown yet.
           'cachemiss'  // cache miss. generally sign to reprocess if seen in front end.
}

export type MaybeSinglePageDetails = SinglePageDetails | SinglePageDetailsErrorState;

export const isSinglePageDetails = (o : MaybeSinglePageDetails) : o is SinglePageDetails => 'guid' in o;


export type LooseSetting = {
    key: string,
    value : string
}

export type UserTokenResponse = {
    user: string,  // user's email address
    key : string,   // auth token.
}

export type Breadcrumb = {
    doc_id: string,
    doc_url : string,
    score : number,
    title : string | undefined,
    last_visited : string | undefined,
    chunk : string  // chunk of content.
}

export type BreadcrumbResponse = Breadcrumb[];


// intended use is to replace indeterminate failure as undefined.
export type BasicError = {error: string}

export function isBasicError(o : any): o is BasicError {
    return 'error' in o;
}


export type PrivacyLevels = "manual" | "allowList" | "allArticles" | "allPages"


export const UnknownDomain = "<unknown>";
