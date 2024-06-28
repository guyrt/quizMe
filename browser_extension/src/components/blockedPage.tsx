import React, { useEffect, useState } from "react"
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine"
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { PrivacyLevels, UnknownDomain } from "../interfaces";

export function BlockedPage() {

    const [privacyLevel, setPrivacyLevel] = useState<PrivacyLevels>("allArticles");

    useEffect(() => {
        new SharedStateReaders().getKVPSetting(SharedStateReaders.PrivacyLevelKey).then(newValue => {
            console.log(`Got privacy level ${newValue}`);
            if (newValue != undefined) {
                setPrivacyLevel(newValue);
            }
        });
    });



    function handleClick() {
        if (privacyLevel == 'allowList') {
            // todo: force allow this domain. Try to auto refresh too...
            
            const payload = {action: "fa_addNewDomainAllow", payload: {domain: UnknownDomain}};
            chrome.runtime.sendMessage(payload, response => {
                console.log(response);
            });
            return;
        }
        fsm.setShowOptions();
    }

    return (
        <div>
            <p>
                {privacyLevel != 'allowList' ? 
                    "This domain is blocked! That means Wezo is not allowed to process the page."
                    : "This domain is not allowed."
                }
            </p>
            <a href="#" onClick={handleClick}>
                Click here to {privacyLevel != 'allowList' ? 
                    "edit your blocked domain."
                    : "allow the domain."
                }
            </a>
            <p>If you've made changes, refresh the page to enable Wezo.</p>
        </div>
    )
}