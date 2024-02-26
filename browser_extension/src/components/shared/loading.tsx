import React, { useState, useEffect } from 'react';

type LoadingGifParams = {
    message: string,
    wait: number // Add the wait parameter here
}

export const LoadingGif: React.FC<LoadingGifParams> = ({ message, wait }) => {
    const [showGif, setShowGif] = useState(false); // Controls the visibility of the gif

    useEffect(() => {
        if (wait > 0) {
            // Set a timeout to show the gif after 'wait' milliseconds
            const timer = setTimeout(() => setShowGif(true), wait);
            // Cleanup the timer if the component unmounts before the timer is up
            return () => clearTimeout(timer);
        } else {
            // Show immediately if wait is 0 or less
            setShowGif(true);
        }
    }, [wait]); // This effect depends on the 'wait' prop

    return (
        <div className="loading-container">
            {showGif ? 
                <>
                    <img className='loading-image' src="./images/worms.gif" alt="Loading"></img>
                    <div style={{ textAlign: 'center' }}>{message}</div>
                </>
                :
                <div style={{ textAlign: 'center' }}>{message}</div>
            }
        </div>
    );
}