import React, { useState } from "react";
import { OptionsWebInterface } from "./optionsWebInterface";
import { useNavigate } from "react-router-dom";

export function Signin() {
    const navigate = useNavigate();

    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [error, setError] = useState<string | null>(null);

    async function signIn() {
        
        console.log("Signin in");
        const status = await new OptionsWebInterface().LoginAndSaveToken(username, password);
        if (status == "ok") {
            navigate("/user"); // off to user settings.
        } else {
            // show an error
            setError("An error occurred while trying to sign in."); // Set error message for other errors
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
                <label htmlFor="username">Email Address</label>
                <input 
                    type="text" 
                    id="username" 
                    onChange={handleUsernameChange} 
                />

                <label htmlFor="password">Password</label>
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
