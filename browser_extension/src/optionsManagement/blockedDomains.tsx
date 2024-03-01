import React, { useEffect, useRef, useState } from "react";
import { SharedStateReaders } from "../stateTrackers/sharedStateReaders";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleStop, faTrashCan } from "@fortawesome/free-regular-svg-icons";


export function BlockedDomains() {
    
    const [domains, setDomains] = useState<string[]>([]);

    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        (new SharedStateReaders()).getDomainBlockList().then((domains : string[]) => {
            setDomains(domains);
        })
    }, []);

    function removeDomainBlock(domain : string) {

    }
    
    const addDomainBlock = async () => {
        const value = inputRef.current?.value;
        if (value == undefined || value == "") {
            return;
        }

        if (domains.findIndex((x) => x === value) > -1) {
            return;
        }

        const payload = {action: "fa_addNewDomainBlock", payload: {domain: value}};
        return new Promise((resolve, reject) => chrome.runtime.sendMessage(payload, 
            function(response) {
                resolve(response.data);
            })
        );
    }

    return (
        <div className="blockedDomains">
            <p>Blocked domains. Every page at these domains will not be stored at all.</p>
            {domains.map(d => <BlockedDomain domain={d} removeDomain={removeDomainBlock}/>)}
            <div className='addDomainBlockSpan'>
                <span className="right-pad">Block a domain:</span>
                <input type="text" ref={inputRef}></input>
                <span className='addDomainBlockButton' onClick={addDomainBlock}><FontAwesomeIcon icon={faCircleStop} /></span>
                <p>(This will delete any stored pages on that domain)</p>
            </div>
        </div>
    );
}


type BlockedDomainProps = {
    domain: string;
    removeDomain : (x : string) => void
};

const BlockedDomain: React.FC<BlockedDomainProps> = ({ domain, removeDomain }) => {

    return (
        <div className="blockedDomainWrapper">
            <span className="option-trashcan"><FontAwesomeIcon icon={faTrashCan} /></span> <span>{domain}</span><span onClick={() => removeDomain(domain)}></span>
        </div>
    )
}
