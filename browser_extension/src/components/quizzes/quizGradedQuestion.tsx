import React from "react";
import { Quiz, QuizQuestion } from "../../interfaces";


export const QuizGraded : React.FC<{
    quiz : Quiz,
    quizAnswers : {[key : number]: number}
}> = ({quiz, quizAnswers}) => {

    const gradeQuiz = () => {
        if (quiz == undefined) {
            return;
        }

        let totalRight = 0;
        for (let i = 0; i < quiz.content.length; i++) {
            const c = quiz.content[i];
            const s = quizAnswers[i] ?? -1;
            if (c.answers[s].correct) {
                totalRight++;
            }
        }
        return totalRight;
    }

    return (
        <div>
            <div>{gradeQuiz()} / {quiz.content.length} correct</div>
            {quiz.content.map((quizQuestion, i) => (
                <QuizGradedQuestion 
                    key={`item_${i}`}
                    question={quizQuestion}
                    questionState={quizAnswers[i]}
                />
            ))}
        </div>
    )
}


const QuizGradedQuestion : React.FC<{
    question: QuizQuestion;
    questionState: number | undefined;
}> = ({question, questionState}) => {

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p
                    key={`item_${i}`}
                    className={
                        `quizAnswer 
                        ${question.answers[i]?.correct ? "selected-correct" : (questionState === i ? "selected-incorrect" : "")}
                        `}

                >
                    {answer.answer}
                </p>
            ))}
        </div>
    )

};