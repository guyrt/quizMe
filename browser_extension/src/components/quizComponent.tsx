import React, {useState, useEffect} from "react";
import { SidePanelState, fsm } from "../stateTrackers/sidePanelStateMachine";
import { Quiz, QuizResponse } from "../interfaces";
import { QuizQuestionState } from "./quizzes/quizInterfaces";
import { QuizQuestionComponent } from "./quizzes/quizQuestion";
import { QuizGradedQuestion } from "./quizzes/quizGradedQuestion";

// Component Props type
type QuizViewProps = {
    quiz: Quiz | undefined;
    finiteState: SidePanelState
}

type QuizState = {
    questions : QuizQuestionState[];

    status : "inprogress" | "scored";
}

// todo - consider splitting this so inner quiz show has a quiz not quiz|undefined
// todo - pass in whether quiz has been answered already.
const QuizView: React.FC<QuizViewProps> = ({ quiz, finiteState}) => {
    const [quizState, setQuizState] = useState<QuizState>({
        questions: quiz?.content.map(() => ({ selected: -1 })) ?? [],
        status: "inprogress"
    });

    useEffect(() => {
        setQuizState({
            questions: quiz?.content.map(() => ({ selected: -1 })) ?? [],
            status: "inprogress"
        });
    }, [quiz]); // Depend on quiz prop

    const handleAnswerClick = (questionIndex: number, answerIndex: number) => {
        setQuizState(prevState => {
            const newQuestions = prevState.questions.map((q, idx) => 
                idx === questionIndex ? { ...q, selected: answerIndex } : q
            );

            return { ...prevState, questions: newQuestions };
        });
    };

    // on quiz submit
    // build an "answered" component that you use.
    const quizSubmit = () => {
        console.log("Quiz submit!");
        setQuizState(prevState => {
            return { ...prevState, status: 'scored' };
        })

        uploadQuiz();
    }

    const gradeQuiz = () => {
        if (quiz == undefined) {
            return;
        }
        let totalRight = 0;
        for (let i = 0; i < quiz.content.length; i++) {
            const c = quiz.content[i];
            const s = quizState.questions[i];
            if (c.answers[s.selected].correct) {
                totalRight++;
            }
        }
        return totalRight;
    }

    const uploadQuiz = () => {
        if (quiz == undefined) {
            return;
        }
        const payload : QuizResponse = {
            quiz_id: quiz.id,
            selection : quizState.questions.map(x => x.selected)
        }
        chrome.runtime.sendMessage({action: "fa_uploadQuizResult", payload: payload})
    }

    function makeQuizClick(forceReload : boolean = false) {
        chrome.runtime.sendMessage({action: "fa_makequiz", payload: {forceReload: forceReload}});
        fsm.setQuizBeingBuilt();
    }

    return (
        <div>
            {finiteState == "QuizBeingDeveloped" ? <div>Building a quiz!</div> : <button onClick={() => makeQuizClick(quiz != undefined)}>
                {quiz != undefined ? "Rebuild" : "Quiz me!"}
            </button>
            }
            {finiteState != "QuizBeingDeveloped" && quiz != undefined && 
            <div>
                {quizState.status == 'inprogress' && <p>Here's your quiz!</p>}
                {quizState.status == 'inprogress' && quiz.content.map((quizQuestion, i) => (
                    <QuizQuestionComponent
                        key={`item_${i}`} 
                        question={quizQuestion} 
                        questionState={quizState.questions[i]}
                        onAnswerClick={(answerIndex) => handleAnswerClick(i, answerIndex)}
                    />
                ))}
                {quizState.status == 'scored' && <div>{gradeQuiz()} / {quiz.content.length} correct</div>}
                {quizState.status == 'scored' && quiz.content.map((quizQuestion, i) => (
                    <QuizGradedQuestion 
                        key={`item_${i}`}
                        question={quizQuestion}
                        questionState={quizState.questions[i]}
                    />
                ))}
                {quizState.status == 'inprogress' && <button onClick={quizSubmit}>How did I do ?!</button>}
            </div>
            }
        </div>
    );
};




export default QuizView;
