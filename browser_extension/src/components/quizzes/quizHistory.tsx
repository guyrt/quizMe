import React from "react";
import { QuizHistory } from "../../interfaces"

type QuizViewProps = {
    quizHistory: QuizHistory
}


const QuizHistoryComponent: React.FC<QuizViewProps> = ({quizHistory}) => {
    
    function simplePlural(input : string, cardinality : number) {
        return input + (cardinality == 1 ? "" : "s");
    }
    
    return (
        <>
            <p>You've gotten points {quizHistory.num_days_month} {simplePlural('day', quizHistory.num_days_month)} this month!</p>
            {quizHistory.streak == 0 ? <p>Start your streak!</p> : <p>Your current streak is {quizHistory.streak} {simplePlural('day', quizHistory.streak)}.</p>}
        </>
    )
};

export default QuizHistoryComponent;