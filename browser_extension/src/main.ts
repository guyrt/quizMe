import { Quiz } from "./interfaces";

class Main {

    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', async () => {
            this.resetQuizTable();
            this.handleIsArticle();
            this.setQuizStart()
        });
    }

    handleIsArticle() {
        const isArticle = true;
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
            chrome.runtime.sendMessage(
                {action: "fa_makequiz", payload: {}},
                this.handleQuiz
            )
        })
    }

    handleQuiz(params : {success : boolean, quiz : Quiz | undefined}) {
        if (params?.success == true) {
            console.log("!!!");
            console.log(params.quiz);
        } else {
            console.log("failed quiz");
        }
    }

}

const m = new Main();

