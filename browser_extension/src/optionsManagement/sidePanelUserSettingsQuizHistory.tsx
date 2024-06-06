import React, { useEffect, useState } from "react";
import { QuizHistory } from "../interfaces";
import { quizHistoryBroker } from "../stateTrackers/sidePanelThread/quizHistoryBroker";

export function SidePanelUserSettingsQuizHistory() {

    const [quizHistory, setQuizHistory] = useState<QuizHistory | undefined>();

    useEffect(() => {
        const l = (state : QuizHistory) => {
            setQuizHistory(state);
        };
        quizHistoryBroker.subscribe(l);

        quizHistoryBroker.trigger();
        
        return () => {
            quizHistoryBroker.unsubscribe(l);
        };
    }, []);

    function stripeClicked() {
        
    }

    return (<>
        {quizHistory != undefined ? 
            <div>
                <p>Nice job! You've got {quizHistory?.total_quizzes} points!</p>
                <p>You currently get {quizHistory?.quiz_allowance} quizzes per month.</p>
                <a href={quizHistory.stripe_redirect} onClick={stripeClicked} target="_blank" rel="noopener noreferrer">Let's get you more!</a>
                <p>This link will take you to Stripe.</p>
            </div> : 
            <p>Checking your points...</p>}
    </>);

}