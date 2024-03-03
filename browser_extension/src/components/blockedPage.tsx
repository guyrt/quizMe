import React from "react"
import { fsm } from "../stateTrackers/sidePanelThread/sidePanelStateMachine"

export function BlockedPage() {

    function handleClick() {
        fsm.setShowOptions();
    }

    return (
        <div>
            <p>
                This domain is blocked! That means Wezo is not allowed to process the page.
            </p>
            <a href="#" onClick={handleClick}>
                Click here to edit your blocked domain.
            </a>
            <p>If you've made changes, refresh the page to enable Wezo.</p>
        </div>
    )
}