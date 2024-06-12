import React, { ChangeEvent, useEffect, useRef, useState } from "react";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import { SidePanelUserSettingsQuizHistory } from "./sidePanelUserSettingsQuizHistory";
import { AllowDomainList, BlockedDomainList } from "./blockedDomains";

import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { PrivacyLevels } from "../interfaces";

export function SidePanelLoggedInUserSettings() {
    
    const [privacyLevel, setPrivacyLevel] = useState<PrivacyLevels>("allArticles");
    const [privacyValue, setPrivacyValue] = useState<number>(3);

    async function logoutThisDevice() {
        // delete your auth token...
        chrome.runtime.sendMessage({action: 'fa_logUserOut'});

        // then redirect to loading.
        fsm.handleUserLoggedOut();
    }
    
    const sharedStateReader = new SharedStateReaders()

    function handlePrivacyChange(newValue : number | number[]) {
        switch (newValue) {
            case 1:
                setPrivacyLevel("manual");
                break;
            case 2:
                setPrivacyLevel("allowList");
                break;
            case 3:
                setPrivacyLevel("allArticles");
                break;
            case 4:
                setPrivacyLevel("allPages");
                break;
            default:
                throw Error("Illegal value");
        }
        setPrivacyValue(newValue);
        //chrome.runtime.sendMessage({action: 'fa_setKVPSetting', payload: {key: 'settings.filtersend', value: newValue}});
    }

    function pickMessage(privacyLevel : PrivacyLevels) : string {
        switch (privacyLevel) {
            case "allArticles":
                return "Wezo will remember articles you visit.";
            case "allPages":
                return "Wezo will remember everything you visit.";
            case "allowList":
                return "Wezo will only remember articles you visit on the sites you allow.";
            case "manual":
                return "Wezo will not remember anything. You can still use Wezo quizzes.";

            default:
                throw Error(`Unexpected privacy ${privacyLevel}`);
        }
    }

    useEffect(() => {
        sharedStateReader.hasApiToken().then(x => {
            if (!x) {
                fsm.handleUserLoggedOut();
            }
        })
    }, []);

    function handleReturnClick() {
        //idea:  store the previous state prior to setting the state to "showSetting"
        //on click, update state back to that previous one; 
        fsm.unsetShowOptions();
    }

    return (
        <>
            <SidePanelUserSettingsQuizHistory />
            <br/>
            <div className="slider-container">
                <Slider 
                    onChange={handlePrivacyChange}
                    included={false}
                    min={1}
                    max={4}
                    step={1}
                    marks={{1: 'manual', 2: 'allowList', 3: 'allArticles', 4: 'allPages'}}
                    value={privacyValue}></Slider>
            </div>
            <br />
            <p>
                {pickMessage(privacyLevel)}
            </p>
            <br/>
            {(privacyValue > 2) && <BlockedDomainList />}
            {(privacyValue < 3) && <AllowDomainList />}

            <div id="buttonsWrapper" className="buttonSettingsWrap">
                <button id='back' className="buttonSettings" onClick={handleReturnClick}>Return</button>
                <button id='logout' className="buttonSettings" onClick={logoutThisDevice}>Log out</button>
            </div>
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