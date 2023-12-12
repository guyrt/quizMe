import React, {useState} from "react";
import { Quiz } from "./interfaces";
import { createRoot } from 'react-dom/client';

import QuizView from "./components/quizComponent";
 
const fakeQuiz = {
    content: [{"question": "What is the main argument presented in the blog post about OpenAI's split?", "answers": [{"answer": "It shows that OpenAI was a non-profit organization."}, {"answer": "The split was a natural progression in the tech industry."}, {"answer": "It is a demonstration of a for-profit company that was incorrectly structured.", "correct": 1}, {"answer": "The split illustrates the success of Microsoft in the AI field."}]}, {"question": "Who benefited from the split of OpenAI according to the blog post?", "answers": [{"answer": "Google"}, {"answer": "Microsoft", "correct": 1}, {"answer": "OpenAI itself"}, {"answer": "The tech industry in general"}]}, {"question": "What does the author imply about the original organization of OpenAI?", "answers": [{"answer": "It was perfectly structured from the start."}, {"answer": "It was organized in a way that was bound to lead to a split.", "correct": 1}, {"answer": "It was a non-profit organization."}, {"answer": "It was too heavily reliant on Microsoft."}]}, {"question": "What is the author's perspective on the outcome of the OpenAI split?", "answers": [{"answer": "It was a successful move for OpenAI."}, {"answer": "It was an unavoidable occurrence in the tech industry."}, {"answer": "It is an example of failure in the organization of a for-profit company.", "correct": 1}, {"answer": "It is a positive event for the overall tech industry."}]}, {"question": "How has Microsoft's position been influenced by the OpenAI split according to the blog post?", "answers": [{"answer": "Microsoft has suffered major losses."}, {"answer": "Microsoft has gained from the fallout by partnering with one faction and hiring the other.", "correct": 1}, {"answer": "Microsoft's position has remained unchanged."}, {"answer": "Microsoft has been forced to reconsider its strategy in the AI field."}]}],
    owner: "",
    id: "",
    reasoning: ""
}

function MainApp() {
    const [isArticle, setIsArticle] = useState<boolean|undefined>(true);

    const [quiz, setQuiz] = useState<Quiz | undefined>();

    const [status, setStatus] = useState<"landing" | "loading" | "error" | "showQuiz">("landing");

    function makeQuizClick() {
        chrome.runtime.sendMessage(
            {action: "fa_makequiz", payload: {}},
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
            <div>App Name</div>
            {status === "landing" ? (
                isArticle ? (
                    <button onClick={makeQuizClick}>Make a quiz</button>
                ) : (
                    <p>This is where we should put your stats? Not an article. Also include a "yes it is" button.</p>
                )
            ) : status === "loading" ? (
                <p>Loading! Be patient...</p>
            ) : status === "showQuiz" && quiz !== undefined ? (
                <QuizView quiz={quiz} />
            ) : (
                <p>Something went wrong :( </p>
            )}
        </>
    );
    
}

// Render your React component instead
const a = document.getElementById('fa-app');
if (a != null) {
    const root = createRoot(a);
    root.render(<MainApp />);
}
