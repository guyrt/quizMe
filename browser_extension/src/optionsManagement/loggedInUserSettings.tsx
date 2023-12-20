import React from "react";
import { useNavigate } from "react-router-dom";
import { OptionsWebInterface } from "./optionsWebInterface";

export function LoggedInUserSettings() {
    
    const navigate = useNavigate();

    async function logoutThisDevice() {
        // delete your auth token...
        new OptionsWebInterface().logoutThisDevice();

        // then redirect to loading.
        navigate("/");
    }
    
    return (
        <div>
            User settings.
            <br/>
            <button id='login' onClick={logoutThisDevice}>Log out</button>
        </div>
    )
}
