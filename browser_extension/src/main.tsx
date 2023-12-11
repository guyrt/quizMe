import React, {useState} from "react";
import { Quiz } from "./interfaces";
import { createRoot } from 'react-dom/client';

function MainApp() {
    const [isArticle, setIsArticle] = useState<boolean|undefined>(true);

    const [quiz, setQuiz] = useState<Quiz | undefined>();

    function makeQuizClick() {
        chrome.runtime.sendMessage(
            {action: "fa_makequiz", payload: {}},
            (x) => handleQuiz(x)
        )

        // make the "loading" screen.
    }

    function handleQuiz(params : {success : boolean, quiz : Quiz | undefined}) {
        if (params?.success == true) {
            console.log("!!!");
            console.log(params.quiz);
        } else {
            console.log("failed quiz");
        }
    }

    return (
        <>
            <div>App Name</div>
            { isArticle && quiz == undefined &&
                <button onClick={makeQuizClick}>Make a quiz</button>
            }
            { isArticle == undefined &&
                <p>Loading...</p>
            }
        </>
    )
}

// Render your React component instead
const a = document.getElementById('fa-app');
if (a != null) {
    const root = createRoot(a);
    root.render(<MainApp />);
}
