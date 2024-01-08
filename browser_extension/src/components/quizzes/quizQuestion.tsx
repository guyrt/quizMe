// Single question including the question and answers.
import React from "react";
import { QuizQuestion } from "../../interfaces";
import { QuizQuestionState } from "./quizInterfaces";


export const QuizQuestionComponent: React.FC<{
    question: QuizQuestion;
    questionState: QuizQuestionState;
    onAnswerClick: (index: number) => void;
}> = ({ question, questionState, onAnswerClick }) => {

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p 
                    onClick={() => onAnswerClick(i)} 
                    key={`item_${i}`}
                    data-index={i} 
                    className={`quizAnswer ${questionState.selected === i ? "selected" : ""}`}
                >
                    {answer.answer}
                </p>
            ))}
        </div>
    );
};