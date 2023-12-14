import React, {useState} from "react";
import { Quiz, QuizQuestion } from "../interfaces";

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

            return { questions: newQuestions, status: prevState.status };
        });
    };

    // on quiz submit
    // build an "answered" component that you use.
    const quizSubmit = () => {

    }

    return (
        <div>
            <p>Here's your quiz!</p>
            {quizState.status == 'inprogress' && quiz.content.map((quizQuestion, i) => (
                <QuizQuestion 
                    question={quizQuestion} 
                    questionState={quizState.questions[i]}
                    onAnswerClick={(answerIndex) => handleAnswerClick(i, answerIndex)}
                />
            ))}
            {quizState.status == 'scored' && quiz.content.map((quizQuestion, i) => (
                <QuizGradedQuestion 
                question={quizQuestion}
                questionState={quizState.questions[i]}
            />
            ))}
            <button onClick={quizSubmit}>How did I do ?!</button>
        </div>
    );
};

const QuizGradedQuestion : React.FC<{
    question: QuizQuestion;
    questionState: QuizQuestionState;
}> = ({question, questionState}) => {

    // clicked answer but not correct... red
    // not clicked but correct ... yellow
    // clicked nad correct ... green.

    return (
        <div className="quizQuestion">
            <p>{question.question}</p>
            {question.answers.map((answer, i) => (
                <p
                    className={`quizAnswer ${questionState.selected === i ? "selected" : ""}`}
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
