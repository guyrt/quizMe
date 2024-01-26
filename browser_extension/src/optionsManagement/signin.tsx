import React, { useState } from "react";
import { OptionsWebInterface } from "./optionsWebInterface";
import { useNavigate } from "react-router-dom";


type SignInProps = {
    doNav : boolean
    handleSignUp: () => void
    handleSignedIn: () => void
}

const SignIn: React.FC<SignInProps> = ({ doNav, handleSignUp, handleSignedIn }) => {

    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [error, setError] = useState<string | null>(null);

    async function signIn() {
        
        const status = await new OptionsWebInterface().loginAndSaveToken(username, password);
        if (status == "ok") {
            if (doNav) {
                const navigate = useNavigate();

                navigate("/user");
            } else {
                handleSignedIn();
            }
        } else {
            // show an error
            setError("Nah dawg, that ain't it. Try again maybe? Type slower?"); // Set error message for other errors
        }
    }

    const handleUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUserName(event.target.value);
    };

    const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(event.target.value);
    };

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
                    onChange={handleUsernameChange} 
                />
                <br/>

                <label htmlFor="password">Password</label>
                <br/>
                <input 
                    type="password" 
                    id="password" 
                    onChange={handlePasswordChange} 
                />

                <button id="save" onClick={signIn}>Sign in!</button>

                {error && <div className="error">{error}</div>}
            </div>
        </>
    );
}

export default SignIn;