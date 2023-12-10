import {state} from "./stateTrackers/appState";

class Main {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', async () => {
            console.log("Start main.js setup.")
            this.resetQuizTable();
            this.hideErrorMessage();
            this.setQuizStart()
        });
    }

    hideErrorMessage() {
        var errorMsgElement = document.getElementById('olive-extension__error-msg');
        if (errorMsgElement) {
            errorMsgElement.classList.remove('olive-extension-showing');
            errorMsgElement.classList.add('olive-extension-hidding');
            errorMsgElement.innerHTML = '';
        }
    }

    showErrorMessage(text : string) {
        var errorMsgElement = document.getElementById('olive-extension__error-msg');
        if (errorMsgElement) {
            errorMsgElement.classList.remove('olive-extension-hidding');
            errorMsgElement.classList.add('olive-extension-showing');
            errorMsgElement.innerHTML = text;
        }
    }
    
    resetQuizTable() {
        var quizTableElement = document.getElementById('olive-extension__email-table');
        if (quizTableElement) {
            quizTableElement.innerHTML = '';
        }
    }
    
    setQuizStart() {
        const btnid = 'faextension__btn-create-quiz';
        const createButton = document.getElementById(btnid);
        if (createButton == null) {
            console.log(`Warning: btn ${btnid} not found.`)
            return
        }
        
        createButton.addEventListener('click',async () => {
            this.hideErrorMessage();
            
            // start api call
            const p = state.getQuiz();
            p.then(x => x?.document);


            // set to loading
        })
    }

    
}

new Main();
