import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

type SignUpProps = {
    doNav : boolean
    handleSignedUp: () => void
}

export const SignUp: React.FC<SignUpProps> = ({ doNav, handleSignedUp }) => {

    const [error, setError] = useState<string | null>(null);

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

        chrome.runtime.sendMessage({action: 'fa_createNewUser', payload: {username: usernameRef, password: passwordRef}}, (response) => {
            if ('error' in response) {
                setError("Something's gone horribly wrong? Try again later.");
            } else {
                if (doNav) {
                    const navigate = useNavigate();
    
                    navigate("/user");
                } else {
                    handleSignedUp();
                }
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
        Welcome!
        <div>
                <label htmlFor="username">Email Address</label>
                <input 
                    type="text" 
                    id="username" 
                    ref={usernameRef}
                />
                <br/>

                <label htmlFor="password">Password</label>
                <input 
                    type="password" 
                    id="password" 
                    ref={passwordRef}
                />
                <br/>

                <label htmlFor="password2">Double check</label>
                <input 
                    type="password" 
                    id="password2"
                    ref={password2Ref}
                    onKeyDown={onPasswordEnterCheck}
                />
                <br/>
                <button id="save" onClick={signUp}>Sign in!</button>
                <br/>
                {error && <div className="error">{error}</div>}
            </div>
        </>
    );
}