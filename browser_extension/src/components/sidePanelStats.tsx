import React, { useEffect, useState } from "react";
import { FilledQuiz, Quiz, VisitHistory } from "../interfaces";
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
                
                //new quiz --> update answers
                if  (localStorage.getItem('quizScored') == null){
                    setQuizAnswers(quiz_context.quiz_results);
                }
                    
            }
            //if complete make changes
            setHistory(activeElement?.uploadedDom?.visit_history);
            
        };

        fsm.subscribe(stateHandler);

        // wrap async and fire a trigger check.
        const f = async () => {await fsm.triggerCheck()};
        f();

        returnSettings();
   
        return () => {
            fsm.unsubscribe(stateHandler);
            
        };

        
    }, []);

    return (
        <div>
            <h3>{header}</h3>

            {(isArticle === true) && 
                <>
                    <QuizView quiz={quiz} finiteState={finiteState} incomingQuizAnswers={quizAnswers} />
                    {process.env.QUIZ_ONLY === 'false' && activeElement?.guid !== undefined && <Breadcrumbs activePage={activeElement.guid}/>}
                </>
            }
            
            {process.env.QUIZ_ONLY === 'false' && history !== undefined && <HistorySection history={history} />}
        </div>
    )


    function returnSettings (){

        const temp_scored = localStorage.getItem('quizScored');
        const temp_quiz = localStorage.getItem('lastQuiz');
        const temp_answers = localStorage.getItem('lastAnswer');

        if (temp_scored != null && temp_quiz != null && temp_answers != null){ 
             
            const scored : Boolean  = JSON.parse(temp_scored);
            const lastQuiz : FilledQuiz = JSON.parse(temp_quiz);
            const answerSelected : number[] = JSON.parse(temp_answers);

            // case quiz has already been answered
            if (scored){
                setQuiz(lastQuiz);
                setQuizAnswers(answerSelected);   
            }
        }
    }
}
