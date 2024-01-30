import React, {useState, useEffect} from "react";
import { Quiz, VisitHistory } from "../interfaces";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import QuizView from "./quizComponent";
import HistorySection from "./history/historySection";


export default function SidePanelStats() {

    const activeElement = fsm.getActiveDetails();

    const [isArticle, setIsArticle] = useState(activeElement?.domClassification?.classification == 'article');

    const [quiz, setQuiz] = useState<Quiz | undefined>(activeElement?.uploadedDom?.quiz_context?.previous_quiz);

    const [header, setHeader] = useState<string>(activeElement?.url.href ?? "Unknown Page")

    const [finiteState, setFiniteState] = useState<SidePanelState>(fsm.getState());

    const [history, setHistory] = useState<VisitHistory>();

    const [quizAnswers, setQuizAnswers] = useState<number[] | undefined>(undefined);

    useEffect(() => {
        const stateHandler = (state : SidePanelState) => {
            const activeElement = fsm.getActiveDetails();

            setFiniteState(state);
            
            console.log("Writing context ", activeElement?.uploadedDom);

            setHeader(activeElement?.title ?? "Unknown page");
            setIsArticle(activeElement?.domClassification?.classification == 'article');
            setQuiz(activeElement?.uploadedDom?.quiz_context?.previous_quiz);
            
            setQuizAnswers(activeElement?.uploadedDom?.quiz_context?.latest_results);
            setHistory(activeElement?.uploadedDom?.visit_history);
        };

        fsm.subscribe(stateHandler);
        // wrap async and fire a trigger check.!
        const f = async () => {await fsm.triggerCheck()};
        f();

        return () => {
            fsm.unsubscribe(stateHandler);
        };
    }, []);

    return (
        <div>
            <h3>{header}</h3>
            <p>This is where we should put your stats. Not an article. Also include a "quiz me" button if not an article.</p>
            {isArticle == true && <QuizView quiz={quiz} finiteState={finiteState} incomingQuizAnswers={quizAnswers}/>}
            {history != undefined && <HistorySection history={history}/>}
        </div>
    )
}