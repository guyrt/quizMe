import React, { useEffect, useState } from "react";
import { QuizHistory } from "../interfaces";
import { quizHistoryBroker } from "../stateTrackers/sidePanelThread/quizHistoryBroker";
import { sharedState } from "../stateTrackers/sharedState";

export function SidePanelUserSettingsQuizHistory() {

    const [quizHistory, setQuizHistory] = useState<QuizHistory | undefined>();
    const [userEmail, setUserEmail] = useState<string | undefined>();

    useEffect(() => {
        const l = (state : QuizHistory) => {
            setQuizHistory(state);
        };
        quizHistoryBroker.subscribe(l);

        quizHistoryBroker.trigger();
        
        sharedState.getUserEmail().then(x => {
            setUserEmail(x);
        })

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
                <p>You currently get {quizHistory?.quiz_allowance} per month.</p>
                <a href={`https://buy.stripe.com/test_eVag2H7Yt6NUdK8fYY?prefilled_email=${userEmail}`} onClick={stripeClicked} target="_blank" rel="noopener noreferrer">Let's get you more!</a>
                <p>This link will take you to Stripe.</p>
            </div> : 
            <p>Checking your points...</p>}
    </>);

}