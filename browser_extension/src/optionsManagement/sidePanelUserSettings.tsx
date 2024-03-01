import React, { ChangeEvent, useEffect, useState } from "react";
import { OptionsWebInterface } from "./optionsWebInterface";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import { SidePanelUserSettingsQuizHistory } from "./sidePanelUserSettingsQuizHistory";
import { BlockedDomains } from "./blockedDomains";

export function SidePanelLoggedInUserSettings() {
    
    async function logoutThisDevice() {
        // delete your auth token...
        new OptionsWebInterface().logoutThisDevice();

        // then redirect to loading.
        fsm.handleUserLoggedOut();
    }
    
    const sharedStateReader = new SharedStateReaders()

    function setFilterToArticles() {
        // todo
    }

    return (
        <>
            <SidePanelUserSettingsQuizHistory />
            <br/>
            <Checkbox label="Track all pages, not just articles?" getter={sharedStateReader.getTrackAllPages} setter={setFilterToArticles} />
            <br/>
            <BlockedDomains />
            <button id='logout' onClick={logoutThisDevice}>Log out</button>
        </>
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