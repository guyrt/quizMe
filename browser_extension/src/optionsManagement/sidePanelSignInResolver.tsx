import React, {useState} from "react";
import SignIn from "./signin";
import { SignUp } from "./signup";
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";


export default function() {

    // true == show log in, false == show sign up.
    const [showLogIn, setShowLogIn] = useState(true);

    async function handleLoggedIn() {
        await fsm.triggerCheck();
    }

    function handleSignUp() {
        setShowLogIn(false);
    }


    return (
        <>
            {showLogIn ? <SignIn 
                doNav={false} 
                handleSignUp={() => handleSignUp()} 
                handleSignedIn={handleLoggedIn} /> : <SignUp doNav={false} handleSwitchToSignIn={() => {setShowLogIn(true)}} handleSignedUp={handleLoggedIn}/>}
        </>
    );
}
