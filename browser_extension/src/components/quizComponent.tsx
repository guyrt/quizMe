import React, {useEffect, useState} from "react";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import { FilledQuiz, Quiz, QuizHistory } from "../interfaces";
import { QuizStatus } from "./quizzes/quizInterfaces";
import { QuizInProgress } from "./quizzes/quizQuestion";
import { QuizGraded } from "./quizzes/quizGradedQuestion";
import { quizHistoryBroker } from "../stateTrackers/sidePanelThread/quizHistoryBroker";
import { LoadingGif } from "./shared/loading";
import QuizHistoryComponent from "./quizzes/quizHistory";

// Component Props type
type QuizViewProps = {
    quiz: Quiz | undefined;
    finiteState: SidePanelState;
    incomingQuizAnswers: number[] | undefined
}


const QuizView: React.FC<QuizViewProps> = ({ quiz, finiteState, incomingQuizAnswers}) => {
    
    const [quizStatus, setQuizStatus] = useState<QuizStatus>("inprogress");
    
    // this maps question idx to answer within that question.
    const [quizAnswers, setQuizAnswers] = useState<{[key: number]: number}>({});

    useEffect(() => {
        if (incomingQuizAnswers != undefined && incomingQuizAnswers.length > 0) {
            const answersObject = incomingQuizAnswers.reduce((obj : {[key: number]: number}, current, index) => {
                obj[index] = current;
                return obj;
            }, {});
            console.log("Answers ", answersObject, incomingQuizAnswers);
            setQuizAnswers(answersObject);
            setQuizStatus("scored");
        } else {
            setQuizStatus("inprogress");
            setQuizAnswers({});
        }
    }, [incomingQuizAnswers]);

    const [quizzesRemaining, setQuizzesRemaining] = useState<number>(Infinity);

    const [quizHistory, setQuizHistory] = useState<QuizHistory>();

    // on start effect
    useEffect(() => {
        

        const stateHandler = (qh : QuizHistory) => {
            // console.log(`Quizhistory state ${qh}`);
            setQuizHistory(qh);
            setQuizzesRemaining(quizHistoryBroker.getQuizzesRemaining());
        };

        quizHistoryBroker.subscribe(stateHandler);
        quizHistoryBroker.trigger();

        return () => {
            quizHistoryBroker.unsubscribe(stateHandler);
        };

    }, []);

    const handleAnswerClick = (questionIndex: number, answerIndex: number) => {
        setQuizAnswers(prevAnswers => {
            return {...prevAnswers, [questionIndex]: answerIndex};
        });
    };

    function makeQuizClick(forceReload : boolean = false) {
      
        // console.log(`I'll remove local data. The current state is  ${fsm.getState()}`);
        localStorage.removeItem('quizScored');
        localStorage.removeItem('lastAnswer');
        localStorage.removeItem('lastQuiz');

        chrome.runtime.sendMessage({action: "fa_makequiz", payload: {forceReload: forceReload}}, (quiz) => {});
    }

    function getMoreQuizzes() {
        fsm.setShowOptions();
    }
   
  
    return (
        <div>
            {/* Handles generation header */}
            {quiz?.status == "building" ?
                <LoadingGif message={"Generating..."} wait={0}/>
                : 
                <>
                    {/* header info */}
                    {quizHistory != undefined && <QuizHistoryComponent quizHistory={quizHistory} />}

                    {quizzesRemaining > 0 &&
                        <div className="buttonWrap">
                            <button className="standard" onClick={() => makeQuizClick(quiz != undefined)}>
                                {quiz?.status != undefined ? "Rebuild" : "Get the point!"}
                            </button>
                        </div>
                    }
                    {
                        quizzesRemaining == Infinity ? <></> : <p className='note-text'>{quizzesRemaining} of {quizHistory?.quiz_allowance} points remaining.</p>
                    }
                    {
                        quizzesRemaining <= 0 ? <div className="buttonWrap"><button className="standard" onClick={getMoreQuizzes}>Get more points!</button></div> : <></>
                    }

                    {/* body */}
                    {quiz?.status == "error" && <div>Sorry something went wrong. Try rebuilding</div>}
                    {quiz == undefined ? 
                        <></> : 
                        quizStatus == "scored" ?
                        <QuizGraded quiz={quiz as FilledQuiz} quizAnswers={quizAnswers} /> :
                        <QuizInProgress quiz={quiz as FilledQuiz} quizAnswers={quizAnswers} setQuizState={setQuizStatus} handleAnswerClick={handleAnswerClick} />
                    }
                </>
            }
            {/* add a function to capture when the quizStatus changes to score */}
            <hr />
        </div>
    );
};

export default QuizView;
