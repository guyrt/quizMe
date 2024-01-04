import React, {useEffect, useState} from "react";
import { createRoot } from 'react-dom/client';

import SidePanelError from "./components/sidePanelError";
import { SidePanelState, fsm } from "./stateTrackers/sidePanelStateMachine";
import SidePanelStats from "./components/sidePanelStats";

function MainApp() {

    const [state, setState] = useState<SidePanelState>("PageNotUploaded");

    // on mount Effects.
    useEffect(() => {
        const stateHandler = (state : SidePanelState) => {
            console.log(`Got state ${state}`);
            setState(state);
        };

        fsm.subscribe(stateHandler);
        fsm.triggerCheck();  // this will end up calling subscribe.

        // Optional cleanup function
        return () => {
            console.log('Main component will unmount');
            fsm.unsubscribe(stateHandler);
        };
    }, []); // Empty dependency array ensures this runs once on mount

    return (
        <>
            {state == "PageNotUploaded" && <p>Loading! Hang tight...</p>}
            {state == "UploadError" && <SidePanelError />}
            {(state == "PageUploadedAndClassified" || state == "QuizBeingDeveloped") && <SidePanelStats />}
        </>
    );
    
}

document.addEventListener('DOMContentLoaded', () => {

    // Render your React component instead
    const a = document.getElementById('fa-app');
    if (a != null) {
        const root = createRoot(a);
        root.render(        
            <MainApp />
        );
    }

});
