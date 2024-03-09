import React from "react";
import { QuizHistory } from "../../interfaces"

type QuizViewProps = {
    quizHistory: QuizHistory
}


const QuizHistoryComponent: React.FC<QuizViewProps> = ({quizHistory}) => {
    return (
        <>
            <p>You've gotten points {quizHistory.num_days_month} day{quizHistory.num_days_month == 1 ? "" : "s"} this month!</p>
            {quizHistory.streak > 0 ? <p>Start your streak!</p> : <p>Your current streak is {quizHistory.streak} days.</p>}
        </>
    )
};

export default QuizHistoryComponent;