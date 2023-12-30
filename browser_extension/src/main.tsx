import React, {useState, useEffect} from "react";
import { Quiz, DomShape } from "./interfaces";
import { createRoot } from 'react-dom/client';

import {log} from "./utils/logger";

import QuizView from "./components/quizComponent";

function MainApp() {
    const [isArticle, setIsArticle] = useState<boolean>(false);

    const [quiz, setQuiz] = useState<Quiz | undefined>();

    const [status, setStatus] = useState<"landing" | "loading" | "error" | "showQuiz">("landing");

    useEffect(() => {
        console.log('Main component initialized.');

        chrome.runtime.sendMessage({action: "fa_checkIsArticle", payload: {}}, (_domFacts : DomShape) => {
            log("fa_checkIsArticle Returned with payload:");
            log(_domFacts);
            setIsArticle(_domFacts?.domClassification.classification == "article");
            setStatus("landing");
        });

        // Optional cleanup function
        return () => {
            console.log('Main component will unmount');
        };
    }, []); // Empty dependency array ensures this runs once on mount


    function makeQuizClick(forceReload : boolean = false) {
        chrome.runtime.sendMessage(
            {action: "fa_makequiz", payload: {forceReload: forceReload}},
            (x) => handleQuiz(x)
        )

        setStatus("loading");
    }

    function handleQuiz(params : {success : boolean, quiz : Quiz | undefined}) {
        if (params?.success == true) {
            console.log("Showing quiz");
            setQuiz(params.quiz);
            setStatus("showQuiz");
        } else {
            console.log("Setting error");
            setStatus("error");
        }
    }

    return (
        <>
            {status === "landing" ? (
                isArticle == true ? (
                    <button onClick={() => makeQuizClick()}>Make a quiz</button>
                ) : (
                    <p>This is where we should put your stats? Not an article. Also include a "yes it is" button.</p>
                )
            ) : status === "loading" ? (
                <p>Loading! Be patient...</p>
            ) : status === "showQuiz" && quiz !== undefined ? (
                <>
                    <button onClick={() => makeQuizClick(true)}>Rebuild</button>
                    <QuizView quiz={quiz} />
                </>
            ) : (
                <>
                    <p>Something went wrong :( </p>
                    <button onClick={() => makeQuizClick()}>Retry</button>
                </>
            )}
        </>
    );
    
}

document.addEventListener('DOMContentLoaded', () => {

    // Render your React component instead
    const a = document.getElementById('fa-app');
    if (a != null) {
        const root = createRoot(a);
        root.render(<MainApp />);
    }

});
