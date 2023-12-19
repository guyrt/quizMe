import React from "react";
import { useNavigate } from "react-router-dom";

export function LoggedInUserSettings() {
    
    const navigate = useNavigate();

    async function logoutThisDevice() {
        // delete your auth token...

        // then redirect to loading.
        navigate("/");
    }
    
    return (
        <div>
            User settings.

            <button id='login' onClick={logoutThisDevice}>Log out</button>
        </div>
    )
}
