// Single question including the question and answers.
import React, {useState} from "react";
import { FilledQuiz, QuizQuestion, QuizResponse } from "../../interfaces";
import { QuizStatus } from "./quizInterfaces";
import { quizHistoryBroker } from "../../stateTrackers/sidePanelThread/quizHistoryBroker";

export const QuizInProgress: React.FC<{
    quiz: FilledQuiz,
    setQuizState : React.Dispatch<React.SetStateAction<QuizStatus>>
    quizAnswers : {[key : number]: number}
    handleAnswerClick : (qIdx: number, aIdx: number) => void
}> = ({quiz, setQuizState, quizAnswers, handleAnswerClick}) => {

    const [isRemoving, setIsRemoving] = useState<boolean>(false);

    function quizSubmit() {

        setIsRemoving(true);
            // Optionally, set a timeout to remove the element from the DOM after animation
        setTimeout(() => {
            setQuizState("scored");
            uploadQuiz();        
        }, 250); // Match the duration of the animation
    }

    const uploadQuiz = () => {
        if (quiz == undefined) {
            return;
        }

        const denseArray = Array.from({length: quiz.content.length}, (_, index) => {
            return index in quizAnswers ? quizAnswers[index] : -1;
        });

        const payload : QuizResponse = {
            quiz_id: quiz.id,
            selection : denseArray
        }
        quizHistoryBroker.uploadQuizResults(payload);
    }

    return (
        <div>
            {quiz.content.map((quizQuestion, i) => (
                <QuizQuestionComponent
                    key={`item_${i}`} 
                    idx={i}
                    question={quizQuestion} 
                    selectedAnswer={quizAnswers[i]}
                    isRemoving={isRemoving}
                    onAnswerClick={(answerIndex) => handleAnswerClick(i, answerIndex)}
                />
            ))}
            <div className="buttonWrap"><button className="standard" onClick={quizSubmit}>How did I do ?!</button></div>
        </div>
    )
}


const QuizQuestionComponent: React.FC<{
    idx: number
    question: QuizQuestion;
    selectedAnswer: number;
    isRemoving: boolean
    onAnswerClick: (index: number) => void;
}> = ({ idx, question, selectedAnswer, isRemoving, onAnswerClick }) => {

    const [animatingAnswer, setAnimatingAnswer] = useState<number | null>(null);

    function handleclick(i : number) {
        setAnimatingAnswer(i);
        onAnswerClick(i)

        // Reset the animation state after a short delay to allow re-animation
        setTimeout(() => setAnimatingAnswer(null), 100); // 500ms matches your CSS animation duration
    }

    return (
        <div className="quizQuestion">
            {/* <span className='quiz-index'>{idx + 1}.</span> */}
            <div className='quizQuestionContent'>
                <span>{question.question}</span>
                {question.answers.map((answer, i) => (
                    <p 
                        onClick={() => handleclick(i)} 
                        key={`item_${i}`}
                        data-index={i} 
                        className={`quizAnswer ${selectedAnswer === i ? "selected" : ""} ${animatingAnswer === i ? 'animate-click' : ''} ${isRemoving ? 'rotate-out-y' : ''}`}
                    >
                        {answer.answer}
                    </p>
                ))}
            </div>
        </div>
    );
};