import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isBasicError } from "../interfaces";


type SignInProps = {
    doNav : boolean
    handleSignUp: () => void
    handleSignedIn: () => void
}

const SignIn: React.FC<SignInProps> = ({ doNav, handleSignUp, handleSignedIn }) => {

    const [error, setError] = useState<string | null>(null);
    const usernameRef = useRef<HTMLInputElement>(null);
    const passwordRef = useRef<HTMLInputElement>(null);


    async function signIn() {
        
        const username = usernameRef.current?.value;
        const password = passwordRef.current?.value;

        if (username == undefined || password == undefined) {
            setError("Something has gone very wrong. Try again later.")
            return;
        }

        chrome.runtime.sendMessage({action: 'fa_signUserIn', payload: {username: username, password: password}}, (response) => {
            if (isBasicError(response)) {
                setError("That ain't it. Try again maybe? Type slower?"); // Set error message for other errors
            } else {
                if (doNav) {
                    const navigate = useNavigate();
    
                    navigate("/user");
                } else {
                    handleSignedIn();
                }
            }
        });

    }

    const onPasswordEnterCheck = (event : React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            signIn();
            return true;
        }
        return false;
    }

    return (
        <>
            <div>
                Sign in!
                <div>
                    <p>New here?</p>
                    <a href='#' onClick={() => handleSignUp()}>Sign up instead (todo fix this in options)</a>
                </div>

                <label htmlFor="username">Email Address</label>
                <br/>
                <input 
                    type="text" 
                    id="username" 
                    ref={usernameRef}
                />
                <br/>

                <label htmlFor="password" >Password</label>
                <br/>
                <input 
                    type="password" 
                    id="password" 
                    ref={passwordRef}
                    onKeyDown={onPasswordEnterCheck}
                />

                <button id="save" onClick={signIn}>Sign in!</button>

                {error && <div className="error">{error}</div>}
            </div>
        </>
    );
}

export default SignIn;