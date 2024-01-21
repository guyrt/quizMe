import React, {useEffect, useState} from "react";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import { Quiz, QuizHistory } from "../interfaces";
import { QuizStatus } from "./quizzes/quizInterfaces";
import { QuizInProgress } from "./quizzes/quizQuestion";
import { QuizGraded } from "./quizzes/quizGradedQuestion";
import { quizHistoryBroker } from "../stateTrackers/sidePanelThread/quizHistoryBroker";

// Component Props type
type QuizViewProps = {
    quiz: Quiz | undefined;
    finiteState: SidePanelState
}


// todo - pass in whether quiz has been answered already.
const QuizView: React.FC<QuizViewProps> = ({ quiz, finiteState}) => {
    
    const [quizStatus, setQuizStatus] = useState<QuizStatus>("inprogress"); // todo load taken quizzes too.
    
    // this maps question idx to answer within that question.
    const [quizAnswers, setQuizAnswers] = useState<{[key: number]: number}>({});

    const [quizzesRemaining, setQuizzesRemaining] = useState<number>(Infinity);

    const [quizHistory, setQuizHistory] = useState<QuizHistory>();

    // on start effect
    useEffect(() => {
        const stateHandler = (qh : QuizHistory) => {
            console.log("Quizhistory state");
            setQuizHistory(qh);
            setQuizzesRemaining(quizHistoryBroker.getQuizzesRemaining());
        };

        quizHistoryBroker.subscribe(stateHandler);
        console.log("Triggering an updated quiz history");
        quizHistoryBroker.trigger();

        return () => {
            quizHistoryBroker.unsubscribe(stateHandler);
        };

    }, []);

    const handleAnswerClick = (questionIndex: number, answerIndex: number) => {
        setQuizAnswers(prevAnswers => {
            return {...quizAnswers, questionIndex: answerIndex};
        });
    };

    function makeQuizClick(forceReload : boolean = false) {
        chrome.runtime.sendMessage({action: "fa_makequiz", payload: {forceReload: forceReload}});
        fsm.setQuizBeingBuilt();
    }

    function getMoreQuizzes() {
        
    }

    return (
        <div>
            {finiteState == "QuizBeingDeveloped" ? 
                <div>Building a quiz!</div> 
                : 
                <>
                    <button onClick={() => makeQuizClick(quiz != undefined)}>
                        {quiz?.status == "error" || quiz != undefined ? "Rebuild" : "Quiz me!"}
                    </button>
                    {
                        quizzesRemaining == Infinity ? <></> : <p className='note-text'>{quizzesRemaining} of {quizHistory?.quiz_allowance} remaining.</p>
                    }                    
                    {
                    quizzesRemaining <= 0 ? <button onClick={getMoreQuizzes}>Get more quizzes</button> : <></>
                    }
                </>
            }
            {finiteState != "QuizBeingDeveloped" && quiz?.status == "error" && <div>Sorry something went wrong. Try rebuilding</div>}
            {finiteState != "QuizBeingDeveloped" && quiz?.status != 'error' && quiz != undefined && quizStatus == "inprogress" && <QuizInProgress quiz={quiz} quizAnswers={quizAnswers} setQuizState={setQuizStatus} handleAnswerClick={handleAnswerClick} />}
            {finiteState != "QuizBeingDeveloped" && quiz?.status != 'error' && quiz != undefined && quizStatus == 'scored' && <QuizGraded quiz={quiz} quizAnswers={quizAnswers} />}
        </div>
    );
};

export default QuizView;
