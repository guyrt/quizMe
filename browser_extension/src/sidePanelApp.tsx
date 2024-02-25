import React, {useEffect, useState} from "react";
import { createRoot } from 'react-dom/client';

import SidePanelError from "./components/sidePanelError";
import { SidePanelState, fsm } from "./stateTrackers/sidePanelThread/sidePanelStateMachine";
import SidePanelStats from "./components/sidePanelStats";
import SidePanelSignInOptions from "./optionsManagement/sidePanelSignInResolver";
import { SidePanelLoggedInUserSettings } from "./optionsManagement/sidePanelUserSettings";

function MainApp() {

    const [state, setState] = useState<SidePanelState>("PageNotUploaded");

    // on mount Effects.
    useEffect(() => {
        const stateHandler = (state : SidePanelState) => {
            console.log(`Got state ${state}`);
            setState(state);
        };

        fsm.subscribe(stateHandler);
        
        // wrap async and fire a trigger check.!
        const f = async () => {await fsm.triggerCheck()};
        f();

        // Optional cleanup function
        return () => {
            console.log('Main component will unmount');
            fsm.unsubscribe(stateHandler);
        };
    }, []); // Empty dependency array ensures this runs once on mount

    function handleSettingsClick() {
        fsm.setShowOptions();
    }
    
    return (
        <>
            {state == "PageNotUploaded" && <p>Loading! Hang tight...</p>}
            {state == "UploadError" && <SidePanelError isError={true}/>}
            {state == "Reload" && <SidePanelError isError={false} />}
            {state == "EmptyPage" && <p>Don't just stand there... open something!</p> }
            {state == "PageUploadedAndClassified" && <SidePanelStats />}
            {state == "PageBlocked" && <p>This page is blocked.</p>}
            {state == "UserLoggedOut" && <div>You are logged out. <SidePanelSignInOptions /></div>}
            {state == "ShowUserSettings" && <SidePanelLoggedInUserSettings />}
            {state != "ShowUserSettings" && 
            <footer className="footer">
                <a href="#" onClick={handleSettingsClick} className="settings-link">Show User Settings</a>
            </footer>
            }
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
