import React from "react";

export default function SidePanelError() {

    const retry = () => {
        // re-fire the event.
        chrome.runtime.sendMessage({action: 'fa_pageLoaded'})
    }
    
    return (
        <div>
            Uh oh! Something went wrong. Our bad. 
            <input type='button' onClick={retry}>Try again?</input>
        </div>
    )
}