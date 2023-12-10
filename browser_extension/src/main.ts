import {state} from "./stateTrackers/appState";
import { ChromeMessage, DomShape } from "./interfaces";


class Main {

    /// Tracker for dom upload requests
    public localRequestId : string = "";

    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', async () => {
            this.resetQuizTable();
            this.handleIsArticle();
            this.setQuizStart()
        });
 
        chrome.runtime.onMessage.addListener((message : ChromeMessage, sender, sendResponse) => {
            console.log(`Got message ${message.action}`);
            if (message.requestId != this.localRequestId) {
                return;
            }

            if (message.action == 'domupload') {
                state.uploadRecord = message.payload.domupload;
                state.isArticle = message.payload.isarticle;
            }
        });

    }

    handleIsArticle() {
        const isArticle = state.isArticle;
        const onlyArticles = document.getElementById('faextension__p-not-available');
        const createButton = document.getElementById('faextension__btn-create-quiz');
        const analyzing = document.getElementById('faextension__p-loading')
        
        const hideClass = 'olive-extension-hidding';

        if (isArticle === undefined) {
            onlyArticles?.classList.add(hideClass);
            createButton?.classList.add(hideClass);
            analyzing?.classList.remove(hideClass);
            return;
        }

        analyzing?.classList.add(hideClass);
        if (isArticle) {
            // show the quiz button
            createButton?.classList.remove(hideClass);
            onlyArticles?.classList.add(hideClass);
        } else {
            // show the "we only work on quizzes"
            createButton?.classList.add(hideClass);
            onlyArticles?.classList.remove(hideClass);
        }
    }

    resetQuizTable() {
        var quizTableElement = document.getElementById('olive-extension__email-table');
        if (quizTableElement) {
            quizTableElement.innerHTML = '';
        }
    }
    
    async setQuizStart() {
        const btnid = 'faextension__btn-create-quiz';
        const createButton = document.getElementById(btnid);
        if (createButton == null) {
            console.log(`Warning: btn ${btnid} not found.`)
            return
        }
        
        createButton.addEventListener('click',async () => {
            // start api call
            const quiz = await state.getQuiz();

            console.log(quiz);
            // set to loading
        })
    }
}

const m = new Main();

/// Startup scripts to load and send DOM. NOTE! this may run too early. So far so good I think
/// but if it happens then you'll need a deferral mechanism. Or give up and just send the DOM when
/// you make your quiz?
chrome.runtime.sendMessage({action: 'fa_pageLoaded'})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action == 'fa_accessDOM') {
        const data : DomShape = {
            dom: document.body.innerHTML.toString(),
            url: document.location,
            recordTime: new Date().getTime(),
            title: document.title,
            requestId : request.requestId
        }
        m.localRequestId = request.requestId;
        sendResponse(data);
    }
})
