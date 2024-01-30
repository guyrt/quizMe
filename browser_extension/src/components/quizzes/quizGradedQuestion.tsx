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
            <div className="quiz-grade-correct">{gradeQuiz()} / {quiz.content.length} correct</div>
            {quiz.content.map((quizQuestion, i) => (
                <QuizGradedQuestion 
                    idx={i}
                    key={`item_${i}`}
                    question={quizQuestion}
                    questionState={quizAnswers[i]}
                />
            ))}
        </div>
    )
}


const QuizGradedQuestion : React.FC<{
    idx: number
    question: QuizQuestion;
    questionState: number | undefined;
}> = ({idx, question, questionState}) => {

    return (
        <div className="quizQuestion">
            <span className='quiz-index'>{idx + 1}.</span>
            <div className='quizQuestionContent'>
                <span>{question.question}</span>
                {question.answers.map((answer, i) => (
                    <p
                        key={`item_${i}`}
                        className={
                            `quizAnswerAnswered
                            ${question.answers[i]?.correct ? "selected-correct" : (questionState === i ? "selected-incorrect" : "")}
                            `}

                    >
                        {answer.answer}
                    </p>
                ))}
            </div>
        </div>
    )

};