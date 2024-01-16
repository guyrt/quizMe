import React, {useState, useEffect} from "react";
import { Quiz } from "../interfaces";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import QuizView from "./quizComponent";


export default function SidePanelStats() {

    const activeElement = fsm.getActiveDetails();

    const [isArticle, setIsArticle] = useState(activeElement?.domClassification?.classification == 'article');

    const [quiz, setQuiz] = useState<Quiz | undefined>(activeElement?.uploadedDom?.quiz_context?.previous_quiz);

    const [header, setHeader] = useState<string>(activeElement?.url.href ?? "Unknown Page")

    const [finiteState, setFiniteState] = useState<SidePanelState>(fsm.getState());

    useEffect(() => {
        const stateHandler = (state : SidePanelState) => {
            const activeElement = fsm.getActiveDetails();

            setFiniteState(state);
            setHeader(activeElement?.title ?? "Unknown page");
            setIsArticle(activeElement?.domClassification?.classification == 'article');
            setQuiz(activeElement?.uploadedDom?.quiz_context?.previous_quiz);
        };

        fsm.subscribe(stateHandler);
        fsm.triggerCheck();  // this will end up calling subscribe.

        return () => {
            fsm.unsubscribe(stateHandler);
        };
    }, []);

    return (
        <div>
            <h3>{header}</h3>
            <p>This is where we should put your stats. Not an article. Also include a "quiz me" button if not an article.</p>
            {isArticle == true && <QuizView quiz={quiz} finiteState={finiteState}/>}
        </div>
    )
}