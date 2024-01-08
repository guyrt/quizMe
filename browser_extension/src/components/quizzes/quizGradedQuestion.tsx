import React from "react";
import { QuizQuestion } from "../../interfaces";
import { QuizQuestionState } from "./quizInterfaces";

export const QuizGradedQuestion : React.FC<{
    question: QuizQuestion;
    questionState: QuizQuestionState;
}> = ({question, questionState}) => {

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p
                    key={`item_${i}`}
                    className={
                        `quizAnswer 
                        ${question.answers[i]?.correct ? "selected-correct" : (questionState.selected === i ? "selected-incorrect" : "")}
                        `}

                >
                    {answer.answer}
                </p>
            ))}
        </div>
    )

};