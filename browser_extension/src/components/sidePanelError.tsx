import React from "react";


type ReloadViewProps = {
    isError : boolean;
}


const ReloadView: React.FC<ReloadViewProps> = ({ isError }) => {

    function retry() {
        // re-fire the event.
        chrome.runtime.sendMessage({action: 'fa_pageLoaded', payload: {url: 'unknown'}})
    }
    
    return (
        <div>
            {isError && <>
                <p>Uh oh! Something went wrong. Our bad.</p> <button type='button' onClick={retry}>
                    Try again?
                </button>
                </>
            }
            {!isError && <p>Let's get you back on track. Reload the page or open something.</p>}
        </div>
    )
}

export default ReloadView
