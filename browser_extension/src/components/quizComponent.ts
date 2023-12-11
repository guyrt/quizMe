class QuizComponent extends HTMLDivElement {
    constructor() {
        super()
    }


}

customElements.define("quiz", QuizComponent, { extends: "div" });
