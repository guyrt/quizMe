class Main {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', async () => {
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
        const createButton = document.getElementById('btn-create-quiz');
        if (createButton == null) {
            return
        }
        
        createButton.addEventListener('click',async () => {
            this.hideErrorMessage();
            
            // start api call

            // set to loading
        })
    }

    
}

new Main();
