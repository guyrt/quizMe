import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isBasicError } from "../interfaces";
import { sendRuntimeMessage } from "../messagePassing/messageProxy";

type SignUpProps = {
    handleSwitchToSignIn: () => void
    handleSignedUp: () => void
}

export const SignUp: React.FC<SignUpProps> = ({ handleSwitchToSignIn, handleSignedUp }) => {

    const [error, setError] = useState<string | null>(null);
    const [showSignIn, setShowSignIn] = useState<boolean>(false);

    const usernameRef = useRef<HTMLInputElement>(null);
    const passwordRef = useRef<HTMLInputElement>(null);
    const password2Ref = useRef<HTMLInputElement>(null);

    async function signUp() {
        
        const username = usernameRef.current?.value;
        const password = passwordRef.current?.value;
        const password2 = password2Ref.current?.value;

        if (username == undefined || password == undefined || password2 == undefined) {
            return;
        }

        if (password != password2) {
            setError("Make sure your passwords match.");
            return;
        }

        sendRuntimeMessage({action: 'fa_createNewUser', payload: {username: username, password: password}}, (response) => {
            if (isBasicError(response)) {
                if (response.error == 'usernameexists') {
                    setError("That email exists in Wezo already! Try logging in.");
                    setShowSignIn(true);
                } else {
                    setError("Something's gone horribly wrong? Try again later.");
                }

            } else {
                handleSignedUp();
            }    
        });

    }

    const onPasswordEnterCheck = (event : React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            signUp();
            return true;
        }
        return false;
    }

    return (
        <>
            <h3>Welcome!</h3>
            <div>
                <label htmlFor="username" className='standard'>Email Address</label>
                <input 
                    className="standard"
                    type="text" 
                    id="username" 
                    ref={usernameRef}
                />
                <br/>

                <label htmlFor="password" className='standard'>Password</label>
                <input 
                    className="standard"
                    type="password" 
                    id="password" 
                    ref={passwordRef}
                />
                <br/>

                <label htmlFor="password2" className='standard'>Re-enter your password.</label>
                <input
                    className="standard" 
                    type="password" 
                    id="password2"
                    ref={password2Ref}
                    onKeyDown={onPasswordEnterCheck}
                />
                <br/>
                <button className="standard" id="save" onClick={signUp}>Sign in!</button>
                <br/>
                {error && <div className="error">{error}</div>}
                {showSignIn && <p><a href='#' onClick={() => handleSwitchToSignIn()}>Click here to sign in.</a></p>}
            </div>
        </>
    );
}