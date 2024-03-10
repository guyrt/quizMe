import React, { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";

export function LoggedInUserSettings() {
    
    const navigate = useNavigate();

    async function logoutThisDevice() {
        // delete your auth token...
        chrome.runtime.sendMessage({action: 'fa_logUserOut'});

        // then redirect to loading.
        navigate("/");
    }

    const sharedStateReader = new SharedStateReaders();

    function handleTrackAllPages() {

    }
    
    return (
        <div>
            User settings.
            <br/>
            <Checkbox label="Track all pages" getter={sharedStateReader.getTrackAllPages} setter={handleTrackAllPages} />
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