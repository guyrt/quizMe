import React, { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { OptionsWebInterface } from "./optionsWebInterface";
import { sharedState } from "../stateTrackers/sharedState";

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
            <br/>
            <Checkbox label="Track all pages" getter={sharedState.getTrackAllPages} setter={sharedState.setFilterSend} />
            <br/>
            <button id='logout' onClick={logoutThisDevice}>Log out</button>
        </div>
    )
}

type CheckboxProps = {
    label: string;
    getter: () => Promise<boolean>;
    setter: (value: boolean) => void;
};

const Checkbox: React.FC<CheckboxProps> = ({ label, getter, setter }) => {

    const [value, setValue] = useState(true);

    useEffect(() => {
        getter().then(x => setValue(x));
    }, 
        []
    )

    function setNewValue(e : ChangeEvent<HTMLInputElement>) {
        const newValue = e.target.checked;
        setValue(newValue);
        setter(newValue);
    }

    return (
        <label>
            {label}
            <input 
                type='checkbox' 
                checked={value}
                onChange={setNewValue}></input>
        </label>
    );
}