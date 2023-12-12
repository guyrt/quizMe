import React, {useState} from "react";
import { Quiz, QuizQuestion } from "../interfaces";

// Component Props type
type QuizViewProps = {
    quiz: Quiz;
}

type QuizState = {
    questions : QuizQuestionState[];
}

type QuizQuestionState = {
    selected : number
}

const QuizView: React.FC<QuizViewProps> = ({ quiz }) => {
    const [quizState, setQuizState] = useState<QuizState>({
        questions: quiz.content.map(() => ({ selected: -1 }))
    });

    const handleAnswerClick = (questionIndex: number, answerIndex: number) => {
        setQuizState(prevState => {
            const newQuestions = prevState.questions.map((q, idx) => 
                idx === questionIndex ? { ...q, selected: answerIndex } : q
            );

            return { questions: newQuestions };
        });
    };

    return (
        <div>
            <p>Here's your quiz!</p>
            {quiz.content.map((quizQuestion, i) => (
                <QuizQuestion 
                    question={quizQuestion} 
                    questionState={quizState.questions[i]}
                    onAnswerClick={(answerIndex) => handleAnswerClick(i, answerIndex)}
                />
            ))}
        </div>
    );
};


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
