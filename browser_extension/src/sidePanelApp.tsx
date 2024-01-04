import React, {useEffect} from "react";
import { createRoot } from 'react-dom/client';

import SidePanelError from "./components/sidePanelError";
import { SidePanelState, fsm } from "./stateTrackers/sidePanelStateMachine";
import { RouterProvider, createMemoryRouter, useNavigate } from "react-router-dom";
import { log } from "./utils/logger";

const sidePanelRouter = createMemoryRouter([
    {
        path: '/',
        element: <MainApp />
    },
    {
        path: "/error",
        element: <SidePanelError />
    },
    {
        path: '/takeQuiz',
    },
    {
        path: '/showStats',
    }
]);

function MainApp() {
    const navigate = useNavigate();

    // on mount Effects.
    useEffect(() => {
        console.log('Main component initialized.');
        const stateHandler = (state : SidePanelState) => {
            log(`Got state ${state}`);
            if (state == 'UploadError') {
                navigate("/error");
            } else if (state == "PageNotUploaded") {
                navigate("/");
            } else if (state == "PageUploadedAndClassified") {
                navigate("/showStats");
            } else {
                Error(`Unexpected state ${state}`);
            }
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
            Loading! Hang tight...
        </>
    );
    
}

document.addEventListener('DOMContentLoaded', () => {

    // Render your React component instead
    const a = document.getElementById('fa-app');
    if (a != null) {
        const root = createRoot(a);
        root.render(        
            <React.StrictMode>
                <RouterProvider router={sidePanelRouter} />
            </React.StrictMode>
        );
    }

});
