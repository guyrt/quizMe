// Single question including the question and answers.
import React from "react";
import { Quiz, QuizQuestion, QuizResponse } from "../../interfaces";
import { QuizStatus } from "./quizInterfaces";

export const QuizInProgress: React.FC<{
    quiz: Quiz,
    setQuizState : React.Dispatch<React.SetStateAction<QuizStatus>>
    quizAnswers : {[key : number]: number}
    handleAnswerClick : (qIdx: number, aIdx: number) => void
}> = ({quiz, setQuizState, quizAnswers, handleAnswerClick}) => {

    function quizSubmit() {
        setQuizState("scored");
        uploadQuiz();
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
        chrome.runtime.sendMessage({action: "fa_uploadQuizResult", payload: payload})
    }

    return (
        <div>
            <p>Here's your quiz!</p>
            {quiz.content.map((quizQuestion, i) => (
                <QuizQuestionComponent
                    key={`item_${i}`} 
                    idx={i}
                    question={quizQuestion} 
                    selectedAnswer={quizAnswers[i]}
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
    onAnswerClick: (index: number) => void;
}> = ({ idx, question, selectedAnswer, onAnswerClick }) => {

    return (
        <div className="quizQuestion">
            <span className='quiz-index'>{idx + 1}.</span>
            <div className='quizQuestionContent'>
                <span>{question.question}</span>
                {question.answers.map((answer, i) => (
                    <p 
                        onClick={() => onAnswerClick(i)} 
                        key={`item_${i}`}
                        data-index={i} 
                        className={`quizAnswer ${selectedAnswer === i ? "selected" : ""}`}
                    >
                        {answer.answer}
                    </p>
                ))}
            </div>
        </div>
    );
};