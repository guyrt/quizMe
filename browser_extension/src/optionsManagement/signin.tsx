import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isBasicError } from "../interfaces";
import { sendRuntimeMessage } from "../messagePassing/messageProxy";


type SignInProps = {
    handleSignUp: () => void
    handleSignedIn: () => void
}

const SignIn: React.FC<SignInProps> = ({ handleSignUp, handleSignedIn }) => {

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

        sendRuntimeMessage({action: 'fa_signUserIn', payload: {username: username, password: password}}, (response) => {
            if (isBasicError(response)) {
                setError("That ain't it. Try again maybe? Type slower?"); // Set error message for other errors
            } else {
                handleSignedIn();
            }
        });

    }

    const innerSignup = () => {
        handleSignUp();
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
                <h3>Let's get you back on track.</h3>
                <div>
                    <p>
                        New here?&nbsp;
                        <a href='#' onClick={() => innerSignup()}>Sign up instead.</a>
                    </p>
                </div>

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
                    onKeyDown={onPasswordEnterCheck}
                />
                <br />
                <button className="standard" id="save" onClick={signIn}>Sign in!</button>

                {error && <div className="error">{error}</div>}
            </div>
        </>
    );
}

export default SignIn;