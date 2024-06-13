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
            console.log("In state handler use effect")
            const activeElement = fsm.getActiveDetails();
            console.log(`about to update FSM with state ${state}`)
            setFiniteState(state);

            console.log("Writing context ", activeElement?.uploadedDom);

            setHeader(activeElement?.title ?? "Unknown page");
            setIsArticle(activeElement?.domClassification?.classification == 'article');
            setQuiz(activeElement?.uploadedDom?.quiz_context);

            const quiz_context = activeElement?.uploadedDom?.quiz_context;
            console.log(`Quiz context status: ${quiz_context?.status}`);
           

            if (quiz_context?.status == 'completed' || quiz_context?.status == "notstarted") {
                console.log(`I will update the answer because quiz is complete to: ${quiz_context.quiz_results} `);
                if  (localStorage.getItem('quizScored') == null){
                    console.log(`Inner if. The current state is  ${fsm.getState()}`);
                    setQuizAnswers(quiz_context.quiz_results);
                }
                else{

                    if(fsm.checkReturn()){
                    console.log(`I'll remove local data. The current state is  ${fsm.getState()}`);
                    localStorage.removeItem('quizScored');
                    }
                    console.log("Outter else");
                }
                    
            }
            //if complete make changes
            setHistory(activeElement?.uploadedDom?.visit_history);

            //add function here to do the check 

            
            
        };

        fsm.subscribe(stateHandler);

        // wrap async and fire a trigger check.
        const f = async () => {await fsm.triggerCheck()};
        f();
        console.log("About to call retSettings");
        returnSettings();
   
        return () => {
            fsm.unsubscribe(stateHandler);
            console.log("In user effect return in sidePanelStats");
            // returnSettings();
            
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

        if (temp_scored == null || temp_quiz == null || temp_answers == null){
                console.log("In if");
                return;
            }
    
        else{
            const scored : Boolean  = JSON.parse(temp_scored);
            const lastQuiz : FilledQuiz = JSON.parse(temp_quiz);
            const answerSelected : number[] = JSON.parse(temp_answers);

            // case quiz has been answered
            if (scored){
                console.log(" In return settings ")
                setQuiz(lastQuiz);
                setQuizAnswers(answerSelected);

                console.log(`In returnSettings lastQuiz ${lastQuiz.content}`);
                console.log(`In returnSettings Answer selected ${answerSelected}`);

                if (localStorage.getItem('quizScored')){
                    // need to clean local variables & 
                    // localStorage.removeItem('quizScored')
                    localStorage.removeItem('lastAnswer')
                    localStorage.removeItem('lastQuiz')
                }
                
            }

            else{
                console.log("In else")
            }
            //fsm trigger is resetting the quiz ? 

            
                
        
    
            }
      
        
    }
}
