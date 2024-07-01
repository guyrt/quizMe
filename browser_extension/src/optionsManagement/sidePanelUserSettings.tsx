import React, { ChangeEvent, useEffect, useRef, useState } from "react";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine";
import { SidePanelUserSettingsQuizHistory } from "./sidePanelUserSettingsQuizHistory";

import { AllowDomainList, BlockedDomainList } from "./blockedDomains";

import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { PrivacyLevels } from "../interfaces";
import { sendRuntimeMessage } from "../messagePassing/messageProxy";


export function SidePanelLoggedInUserSettings() {
    
    const [privacyLevel, setPrivacyLevel] = useState<PrivacyLevels>("allArticles");
    const [privacyValue, setPrivacyValue] = useState<number>(3);

    async function logoutThisDevice() {
        // delete your auth token...
        sendRuntimeMessage({action: 'fa_logUserOut', payload: {}});

        // then redirect to loading.
        fsm.handleUserLoggedOut();
    }
    
    const sharedStateReader = new SharedStateReaders()

    function _mapLevelToValue(level : PrivacyLevels) {
        switch (level) {
            case 'allArticles': 
                return 3;
            case 'allPages': 
                return 4;
            case 'allowList': 
                return 2;
            case 'manual': 
                return 1;
            default:
                throw Error(`Unexpected privacy ${level}`);
        }
    }

    function handlePrivacyChange(newValue : number | number[]) {
        let privacyLevel : PrivacyLevels = "manual";
        switch (newValue) {
            case 1:
                privacyLevel = "manual";
                break;
            case 2:
                privacyLevel = "allowList";
                break;
            case 3:
                privacyLevel = "allArticles";
                break;
            case 4:
                privacyLevel = "allPages";
                break;
            default:
                throw Error("Illegal value");
        }
        setPrivacyLevel(privacyLevel);
        setPrivacyValue(newValue);
        sendRuntimeMessage({action: 'fa_setKVPSetting', payload: {key: SharedStateReaders.PrivacyLevelKey, value: privacyLevel}});
    }

    function pickMessage(level : PrivacyLevels) : string {
        switch (level) {
            case "allArticles":
                return "Wezo will remember articles you visit.";
            case "allPages":
                return "Wezo will remember everything you visit.";
            case "allowList":
                return "Wezo will only remember articles you visit on the sites you allow.";
            case "manual":
                return "Wezo will not remember anything. You can still use Wezo quizzes.";

            default:
                throw Error(`Unexpected privacy ${level}`);
        }
    }

    useEffect(() => {
        // load privacy and set both values.
        new SharedStateReaders().getKVPSetting(SharedStateReaders.PrivacyLevelKey).then(newValue => {
            console.log(`Got privacy level ${newValue}`);
            if (newValue != undefined) {
                setPrivacyLevel(newValue);
                const v = _mapLevelToValue(newValue);
                console.log(`Got privacy level ${v}`);
                setPrivacyValue(v);
            }
        });
        
        sharedStateReader.hasApiToken().then(x => {
            if (!x) {
                fsm.handleUserLoggedOut();
            }
        });

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