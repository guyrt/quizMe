import React, {useState} from "react";
import { Quiz } from "../interfaces";
import { fsm } from "../stateTrackers/sidePanelStateMachine";
import QuizView from "./quizComponent";


export default function SidePanelStats() {

    const activeElement = fsm.getActiveDetails();

    const [isArticle, setIsArticle] = useState(activeElement?.domClassification.classification == 'article');

    const [quiz, setQuiz] = useState<Quiz | undefined>(activeElement?.uploadedDom?.quiz_context?.previous_quiz);

    return (
        <div>
            <p>This is where we should put your stats. Not an article. Also include a "quiz me" button if not an article.</p>
            {isArticle == true && <QuizView quiz={quiz} setQuiz={setQuiz}/>}
        </div>
    )
}