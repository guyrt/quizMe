import React, { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";


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

    function handleReturnClick(){
        fsm.unsetShowOptions();
          //it'll probably be the same logic of the sidePanelUserSettings.tsx
    }
    
    return (
        <div>
            User settings.
            <br/>
            <Checkbox label="Track all pages" getter={sharedStateReader.getTrackAllPages} setter={handleTrackAllPages} />
            <br/>
            <div id="buttonsWrapper" className="buttonSettingsWrap">
                <button id='back' className="buttonSettings" onClick={handleReturnClick}>Return Home</button>
                <button id='logout' className="buttonSettings" onClick={logoutThisDevice}>Log out</button>
            </div>
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