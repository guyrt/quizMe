import React, { ChangeEvent } from "react";
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

    async function setFilterSend(e : ChangeEvent<HTMLInputElement>) {
        e.target.value;
    }
    
    return (
        <div>
            User settings.
            <input type='checkbox' onChange={setFilterSend}></input>
            <br/>
            <button id='logout' onClick={logoutThisDevice}>Log out</button>
        </div>
    )
}
