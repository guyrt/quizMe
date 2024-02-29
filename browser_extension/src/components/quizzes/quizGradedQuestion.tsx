import React from "react";
import { FilledQuiz, QuizQuestion } from "../../interfaces";


export const QuizGraded : React.FC<{
    quiz : FilledQuiz,
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
            if (c.answers[s]?.correct) {
                totalRight++;
            }
        }
        return totalRight;
    }

    return (
        <div>
            {quiz.content.map((quizQuestion, i) => (
                <QuizGradedQuestion 
                    idx={i}
                    key={`item_${i}`}
                    question={quizQuestion}
                    questionState={quizAnswers[i]}
                />
            ))}
            <div className="quiz-grade-correct">{gradeQuiz()} / {quiz.content.length} correct</div>
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
            <div className='quizQuestionContent'>
                <span>{question.question}</span>
                {question.answers.map((answer, i) => (
                    <p
                        key={`item_${i}`}
                        className={
                            `quizAnswerAnswered
                            ${question.answers[i]?.correct ? "selected-correct rotate-in-y-slow" : (questionState === i ? "selected-incorrect" : "")}
                            rotate-in-y
                            `}

                    >
                        {answer.answer}
                    </p>
                ))}
            </div>
        </div>
    )

};