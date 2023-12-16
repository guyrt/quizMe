import React, {useState} from "react";
import { Quiz, QuizQuestion, QuizResponse } from "../interfaces";

// Component Props type
type QuizViewProps = {
    quiz: Quiz;
}

type QuizState = {
    questions : QuizQuestionState[];

    status : "inprogress" | "scored";
}

type QuizQuestionState = {
    selected : number
}

const QuizView: React.FC<QuizViewProps> = ({ quiz }) => {
    const [quizState, setQuizState] = useState<QuizState>({
        questions: quiz.content.map(() => ({ selected: -1 })),
        status: "inprogress"
    });

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
        const payload : QuizResponse = {
            quiz_id: quiz.id,
            selection : quizState.questions.map(x => x.selected)
        }
        chrome.runtime.sendMessage({action: "fa_uploadQuizResult", payload: payload})
    }

    return (
        <div>
            {quizState.status == 'inprogress' && <p>Here's your quiz!</p>}
            {quizState.status == 'inprogress' && quiz.content.map((quizQuestion, i) => (
                <QuizQuestion 
                    question={quizQuestion} 
                    questionState={quizState.questions[i]}
                    onAnswerClick={(answerIndex) => handleAnswerClick(i, answerIndex)}
                />
            ))}
            {quizState.status == 'scored' && <div>{gradeQuiz()} / {quiz.content.length} correct</div>}
            {quizState.status == 'scored' && quiz.content.map((quizQuestion, i) => (
                <QuizGradedQuestion 
                question={quizQuestion}
                questionState={quizState.questions[i]}
            />
            ))}
            {quizState.status == 'inprogress' && <button onClick={quizSubmit}>How did I do ?!</button>}
        </div>
    );
};

const QuizGradedQuestion : React.FC<{
    question: QuizQuestion;
    questionState: QuizQuestionState;
}> = ({question, questionState}) => {

    // clicked answer but not correct... red
    // correct ... green.

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p
                    className={`quizAnswer ${questionState.selected === i ? (question.answers[i]?.correct ? "selected-correct" : "selected-incorrect") : ""}`}
                >
                    {answer.answer}
                </p>
            ))}
        </div>
    )

};

// Single question including the question and answers.
const QuizQuestion: React.FC<{
    question: QuizQuestion;
    questionState: QuizQuestionState;
    onAnswerClick: (index: number) => void;
}> = ({ question, questionState, onAnswerClick }) => {

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p onClick={() => onAnswerClick(i)} data-index={i} 
                    className={`quizAnswer ${questionState.selected === i ? "selected" : ""}`}
                >
                    {answer.answer}
                </p>
            ))}
        </div>
    );
};

export default QuizView;
