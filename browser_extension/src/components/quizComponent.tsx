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

export const QuizView: React.FC<QuizViewProps> = ({ quiz }) => {

    const [quizState, setQuizState] = useState<QuizState>({
        questions: quiz.content.map<QuizQuestionState>((x, i) => {
            return { selected: -1 }})
    });

    return (
        <div>
            <p>Here's your quiz!</p>
            {quiz.content.map((quizQuestion, i) => <QuizQuestion question={quizQuestion} questionState={quizState.questions[i]}></QuizQuestion>)}
        </div>

    )
}

const QuizQuestion : React.FC<{question : QuizQuestion, questionState : QuizQuestionState}> = ({question, questionState}) => {
    
    function answerClicked(index : number) {
        questionState.selected = index;
    }

    return (
        <div>
            <p>{question.question}</p>
            { question.answers.map((answer, i) => 
                <p onClick={() => answerClicked(i)} data-index={i} 
                    className={questionState.selected == i ? "selected" : ""}
                >{answer.answer}</p>
            )}
        </div>
    )
}

export default QuizView;
