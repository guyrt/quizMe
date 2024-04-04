import React, { useEffect, useState } from "react";
import { Quiz, VisitHistory } from "../interfaces";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import HistorySection from "./history/historySection";
import QuizView from "./quizComponent";
import Breadcrumbs from "./history/breadcrumbs";


export default function SidePanelStats() {

    const activeElement = fsm.getActiveDetails();

    const [isArticle, setIsArticle] = useState(activeElement?.domClassification?.classification == 'article');

    const [quiz, setQuiz] = useState<Quiz | undefined>(activeElement?.uploadedDom?.quiz_context);

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
            setQuiz(activeElement?.uploadedDom?.quiz_context);

            const quiz_context = activeElement?.uploadedDom?.quiz_context;
            if (quiz_context?.status == 'completed' || quiz_context?.status == "notstarted") {
                setQuizAnswers(quiz_context.quiz_results);
            }

            setHistory(activeElement?.uploadedDom?.visit_history);
        };

        fsm.subscribe(stateHandler);

        // wrap async and fire a trigger check.
        const f = async () => {await fsm.triggerCheck()};
        f();

        return () => {
            fsm.unsubscribe(stateHandler);
        };
    }, []);

    return (
        <div>
            <h3>{header}</h3>

            {(isArticle === true) && <>
                    <QuizView quiz={quiz} finiteState={finiteState} incomingQuizAnswers={quizAnswers} />
                    {activeElement?.guid !== undefined && <Breadcrumbs activePage={activeElement.guid}/>}
                </>
            }
            {history !== undefined && <HistorySection history={history} />}
        </div>
    )
}