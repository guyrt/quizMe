import React from "react";

export default function SidePanelError() {

    function retry() {
        // re-fire the event.
        chrome.runtime.sendMessage({action: 'fa_pageLoaded'})
    }
    
    return (
        <div>
            Uh oh! Something went wrong. Our bad. 
            <button type='button' onClick={retry}>Try again?</button>
        </div>
    )
}