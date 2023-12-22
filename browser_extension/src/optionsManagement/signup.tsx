import React, { useState } from "react";
import { OptionsWebInterface } from "./optionsWebInterface";
import { useNavigate } from "react-router-dom";

export function SignUp() {

    const navigate = useNavigate();

    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [password2, setPassword2] = useState<string>("");
    const [error, setError] = useState<string | null>(null);

    async function signUp() {
        
        if (password != password2) {
            setError("Make sure your passwords match.");
            return;
        }

        const status = await new OptionsWebInterface().signUpAndSaveToken(username, password);
        if (status == "ok") {
            navigate("/user"); // off to user settings.
        } else {
            // show an error
            setError("Something's gone horribly wrong? Try again later."); // Set error message for other errors
        }
    }

    const handleUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUserName(event.target.value);
    };

    const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(event.target.value);
    };

    const handlePasswordChange2 = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPassword2(event.target.value);
    };

    return (
        <>
        Welcome!
        <div>
                <label htmlFor="username">Email Address</label>
                <input 
                    type="text" 
                    id="username" 
                    onChange={handleUsernameChange} 
                />
                <br/>

                <label htmlFor="password">Password</label>
                <input 
                    type="password" 
                    id="password" 
                    onChange={handlePasswordChange} 
                />
                <br/>

                <label htmlFor="password2">Double check</label>
                <input 
                    type="password" 
                    id="password2"
                    onChange={handlePasswordChange2} 
                />
                <br/>
                <button id="save" onClick={signUp}>Sign in!</button>
                <br/>
                {error && <div className="error">{error}</div>}
            </div>
        </>
    );
}