import React, { useEffect, useState } from "react";
import { QuizHistory } from "../interfaces";
import { quizHistoryBroker } from "../stateTrackers/sidePanelThread/quizHistoryBroker";

export function SidePanelUserSettingsQuizHistory() {

    const [quizLoaded, setQuizLoaded] = useState<boolean>(false);
    const [quizHistory, setQuizHistory] = useState<QuizHistory | undefined>();

    useEffect(() => {
        quizHistoryBroker.subscribe((state : QuizHistory) => {
            setQuizHistory(state);
            setQuizLoaded(true);
        });

        quizHistoryBroker.trigger();
    }, []);

    return (<>
        {quizLoaded ? 
            <div>
                <p>Nice job! You've got {quizHistory?.total_quizzes} points!</p>
                <p>You currently get {quizHistory?.quiz_allowance} per month.</p>
                <a href="https://buy.stripe.com/test_eVag2H7Yt6NUdK8fYY" target="_">Let's get you more!</a>
                <p>This link will take you to Stripe.</p>
            </div> : 
            <p>Checking your points...</p>}
    </>);

}