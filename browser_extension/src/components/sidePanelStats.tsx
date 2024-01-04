import React, {useState} from "react";
import { Quiz } from "../interfaces";
import { fsm } from "../stateTrackers/sidePanelStateMachine";


export default function SidePanelStats() {

    const activeElement = fsm.getActiveDetails();

    const [isArticle, setIsArticle] = useState(activeElement?.domClassification.classification == 'article');

    const [quiz, setQuiz] = useState<Quiz | undefined>(activeElement?.uploadedDom?.quiz_context?.previous_quiz);


    function makeQuizClick(forceReload : boolean = false) {
        chrome.runtime.sendMessage({action: "fa_makequiz", payload: {forceReload: forceReload}})
            .then((x) => handleQuiz(x));

    }

    function handleQuiz(params : {success : boolean, quiz : Quiz | undefined}) {
        if (params?.success == true) {
            console.log("Showing quiz");
            setQuiz(params.quiz);
        } else {
            console.log("Setting error");
        }
    }

    return (
        <div>
            <p>This is where we should put your stats. Not an article. Also include a "quiz me" button if not an article.</p>
            isArticle == true && <button onClick={() => makeQuizClick()}>Make a quiz</button>
        </div>
    )
}